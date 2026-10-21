"""Exercise observable batching, races, cancellations and resource closeout locally."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import uuid

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import task_inbox as inbox
from queue_result import deliver

THREAD = '00000000-0000-4000-8000-000000000001'
REMOTE = 'unix:///tmp/disposable-inbox-test.sock'


class InboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mailbox = self.root / 'inbox'
        self.queue = {}
        self.sends = []
        self.send_patch = patch.object(inbox, 'submit', side_effect=self.submit)
        self.retire_patch = patch.object(inbox, 'retire', side_effect=self.retire)
        self.send_patch.start(); self.retire_patch.start()
        self.addCleanup(self.send_patch.stop); self.addCleanup(self.retire_patch.stop)
        inbox.initialize(self.mailbox, 'fixture', THREAD, REMOTE)

    def submit(self, **args):
        identity = str(uuid.uuid4())
        self.queue[identity] = args['message']
        self.sends.append(identity)
        return {'status': 'accepted', 'stdout': f'Queued message {identity} for thread {THREAD}.', 'returncode': 0}

    def retire(self, remote, thread, wake):
        self.assertEqual((remote, thread), (REMOTE, THREAD))
        identity = wake['queue_id']
        if identity not in self.queue:
            return 'absent_or_started'
        self.assertEqual(self.queue.pop(identity), wake['message'])
        return 'deleted'

    def publish(self, identity, body='result', **changes):
        path = self.root / (identity + '.txt')
        if not path.exists():
            path.write_text(body)
        args = dict(task='fixture', delivery_id=identity, sender='reviewer', thread=THREAD,
                    artifact=path, version='candidate-1', summary='review result',
                    outbox=self.root/'outbox', mailbox=self.mailbox)
        args.update(changes)
        return deliver(**args)

    def op(self, action, **args):
        return inbox.operate(self.mailbox, action, **args)

    def ack(self, identity):
        digest = hashlib.sha256((self.root/(identity+'.txt')).read_bytes()).hexdigest()
        return self.op('ack', delivery_id=identity, sha256=digest, disposition='reviewed and reconciled')

    def test_active_many_rounds_never_queue_and_wait_returns_ready(self):
        for i in range(18): self.publish(f'r{i}')
        self.assertEqual(self.sends, [])
        self.assertEqual(len(self.op('take')['results']), 18)
        self.assertTrue(self.op('wait')['ready'])
        for i in range(18): self.ack(f'r{i}')
        self.assertEqual(self.op('wait')['mode'], 'waiting')
        self.assertEqual(self.sends, [])

    def test_parallel_completed_gates_share_one_wakeup(self):
        self.op('wait')
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda i:self.publish(f'gate{i}'), range(12)))
        self.assertEqual(len(self.sends), 1)
        self.assertEqual(len(self.op('take')['results']), 12)
        self.assertFalse(self.queue)

    def test_proactive_consumption_retires_only_owned_wakeup(self):
        self.queue['unrelated-user-input'] = 'user task'
        self.op('wait'); self.publish('round1')
        self.ack('round1')
        self.assertEqual(self.queue, {'unrelated-user-input':'user task'})
        self.assertEqual(self.op('take')['results'], [])

    def test_consumed_wakeup_and_arrivals_during_work_do_not_requeue(self):
        self.op('wait'); self.publish('round1')
        self.queue.clear()  # The host started the notification turn.
        self.op('take'); self.publish('round2'); self.ack('round1')
        self.assertEqual(len(self.sends), 1)
        self.assertTrue(self.op('wait')['ready'])
        self.ack('round2'); self.op('wait'); self.publish('round3')
        self.assertEqual(len(self.sends), 2)

    def test_publish_racing_wait_is_either_ready_or_notified(self):
        for i in range(20):
            with ThreadPoolExecutor(max_workers=2) as pool:
                a=pool.submit(self.op,'wait');b=pool.submit(self.publish,f'race{i}')
                wait=a.result();b.result()
            state=self.op('status')
            self.assertTrue(wait.get('ready') or state['wake'] is not None)
            self.ack(f'race{i}')

    def test_stable_id_replay_preserves_disposition_and_changed_payload_fails(self):
        self.publish('same');self.ack('same');self.publish('same')
        self.assertEqual(self.op('take')['results'], [])
        with self.assertRaises(RuntimeError): self.publish('same', version='candidate-2')

    def test_wrong_membership_or_hash_does_not_acknowledge(self):
        with self.assertRaises(ValueError): self.publish('other',task='other-task')
        self.publish('own')
        with self.assertRaises(ValueError): self.op('ack',delivery_id='own',sha256='0'*64,disposition='done')
        (self.root/'own.txt').write_text('changed after publication')
        with self.assertRaises(ValueError):self.ack('own')
        self.assertEqual(len(self.op('take')['results']),1)

    def test_unknown_send_retains_all_results_and_never_retries(self):
        self.op('wait')
        with patch.object(inbox,'submit',return_value={'status':'uncertain','error':'timeout'}) as submit:
            with self.assertRaises(RuntimeError):self.publish('one')
            with self.assertRaises(RuntimeError):self.publish('two')
            with self.assertRaises(RuntimeError):self.op('take')
            self.assertEqual(submit.call_count,1)
        self.assertEqual(len(self.op('status')['results']),2)

    def test_failed_cleanup_retains_exact_wake_for_safe_retry(self):
        self.op('wait');self.publish('one')
        with patch.object(inbox,'retire',side_effect=TimeoutError('offline')):
            with self.assertRaises(TimeoutError):self.op('take')
        self.assertEqual(self.op('status')['mode'],'active')
        self.assertIsNotNone(self.op('status')['wake'])
        self.op('take');self.assertFalse(self.queue)

    def test_pause_wins_over_results_and_take_until_explicit_resume(self):
        self.op('wait');self.publish('before');self.op('pause');self.publish('after')
        self.assertFalse(self.queue)
        with self.assertRaises(RuntimeError):self.op('take')
        with self.assertRaises(RuntimeError):self.op('wait')
        self.op('resume');self.assertEqual(len(self.op('take')['results']),2)
        self.assertEqual(len(self.sends),1)

    def test_stop_before_publication_does_not_create_a_result(self):
        with self.assertRaises(RuntimeError):self.publish('cancelled',cancelled=lambda:True)
        self.assertEqual(self.op('take')['results'],[])

    def test_close_requires_dispositions_and_fresh_resource_removal(self):
        identity=str(uuid.uuid4())
        self.op('terminal-add',terminal_id=identity,state_dir=self.root/'watch')
        self.publish('result')
        with self.assertRaises(RuntimeError):self.op('close')
        self.ack('result')
        with self.assertRaises(RuntimeError):self.op('close')
        snapshot=self.root/'snapshot.json'
        raw={'scope':'all','captured_at':datetime.now(timezone.utc).isoformat(),'terminals':[{'id':identity}]}
        snapshot.write_text(json.dumps(raw));self.op('terminals-reconcile',snapshot=snapshot)
        with self.assertRaises(RuntimeError):self.op('close')
        raw.update(terminals=[],captured_at=(datetime.now(timezone.utc)-timedelta(minutes=2)).isoformat())
        snapshot.write_text(json.dumps(raw))
        with self.assertRaises(ValueError):self.op('terminals-reconcile',snapshot=snapshot)
        raw['captured_at']=datetime.now(timezone.utc).isoformat();snapshot.write_text(json.dumps(raw))
        self.op('terminals-reconcile',snapshot=snapshot);self.assertEqual(self.op('close')['mode'],'closed')
        with self.assertRaises(RuntimeError):self.publish('late')
        with self.assertRaises(RuntimeError):self.op('resume')

    def test_new_cli_flags_and_original_terminal_add_remain_usable(self):
        command = [sys.executable, str(SCRIPTS/'task_inbox.py'), '--mailbox', str(self.mailbox)]
        identity = str(uuid.uuid4())
        added = subprocess.run(command+['terminal-add', '--terminal-id', identity,
                                      '--state-dir', str(self.root/'watch'), '--brief'],
                               capture_output=True, text=True)
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assertNotIn('terminals', json.loads(added.stdout))
        summary = subprocess.run(command+['status', '--summary'], capture_output=True, text=True)
        self.assertEqual(summary.returncode, 0, summary.stderr)
        self.assertEqual(json.loads(summary.stdout)['resources'][0]['terminal_id'], identity)
        rejected = subprocess.run(command+['status', '--terminal-id', identity], capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)

    def handoff(self, **changes):
        new = '00000000-0000-4000-8000-000000000002'
        value = dict(migration_id='move-1', task='fixture', old_thread=THREAD,
                     new_thread=new, publishers_drained=True, old_consumer_released=True,
                     evidence=['host-checkpoint.json'])
        value.update(changes)
        path = self.root/'handoff.json'
        path.write_text(json.dumps(value))
        return dict(expected_thread=THREAD, new_thread=new,
                    expected_state_sha256=self.op('status', summary=True)['state_sha256'], handoff=path)

    def test_status_missing_mailbox_or_lock_never_creates_files(self):
        for summary in (False, True):
            absent = self.root/'missing-parent'/'mailbox'
            before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
            with self.assertRaises(FileNotFoundError):
                inbox.operate(absent, 'status', summary=summary)
            self.assertEqual(sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*')), before)
            unlocked = self.root/'unlocked'
            unlocked.mkdir(exist_ok=True)
            (unlocked/'state.json').write_text('{}')
            before = {str(p.relative_to(self.root)): p.read_bytes()
                      for p in self.root.rglob('*') if p.is_file()}
            with self.assertRaises(FileNotFoundError):
                inbox.operate(unlocked, 'status', summary=summary)
            self.assertEqual({str(p.relative_to(self.root)): p.read_bytes()
                              for p in self.root.rglob('*') if p.is_file()}, before)
            self.assertFalse((unlocked/'lock').exists())

    def test_registered_status_uses_existing_lock_without_changing_lifecycle(self):
        for mode in ('active', 'paused', 'closed'):
            if mode == 'paused':
                self.op('pause')
            elif mode == 'closed':
                self.op('resume'); self.op('close')
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                      for p in self.mailbox.iterdir() if p.is_file()}
            original_flock = inbox.fcntl.flock
            with patch.object(inbox.fcntl, 'flock', wraps=original_flock) as flock:
                self.assertEqual(self.op('status')['mode'], mode)
                self.assertEqual(self.op('status', summary=True)['mode'], mode)
            self.assertEqual(flock.call_count, 4)  # Each read acquires and releases the same lock.
            self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                              for p in self.mailbox.iterdir() if p.is_file()}, before)

    def test_summary_is_read_only_and_explicit_about_unverified_facts(self):
        self.op('wait'); self.publish('one')
        before = (self.mailbox/'state.json').read_bytes()
        (self.root/'one.txt').write_text('not checked by summary')
        report = self.op('status', summary=True)
        self.assertEqual((self.mailbox/'state.json').read_bytes(), before)
        self.assertEqual(report['mode'], 'waiting')
        self.assertEqual(report['pending'][0]['delivery_id'], 'one')
        self.assertEqual(report['state_sha256'], hashlib.sha256(before).hexdigest())
        self.assertIn('artifact bytes and candidate equivalence', report['not_checked'])
        self.assertTrue(self.queue)
        self.op('pause')
        self.assertEqual(self.op('status', summary=True)['mode'], 'paused')

    def test_summary_separates_result_observer_and_resource_and_skips_history(self):
        identity = str(uuid.uuid4()); state_dir = self.root/'watch'
        state_dir.mkdir()
        (state_dir/'binding.json').write_text(json.dumps({'expect':'one', 'pid':123}))
        (state_dir/'status.json').write_text(json.dumps({'phase':'watching'}))
        self.op('terminal-add', terminal_id=identity, state_dir=state_dir)
        self.publish('one'); self.ack('one')
        snapshot = self.root/'all.json'
        snapshot.write_text(json.dumps({'scope':'all','captured_at':datetime.now(timezone.utc).isoformat(),'terminals':[]}))
        self.op('terminals-reconcile', snapshot=snapshot)
        with patch('observer.inspect_state', side_effect=AssertionError('do not scan removed history')):
            self.assertEqual(self.op('status', summary=True)['resources'], [])
        report = self.op('status', summary=True, terminal_id=[identity])
        item = report['resources'][0]
        self.assertEqual(item['terminal_status'], 'removed')
        self.assertEqual(item['expected_result'], 'processed')
        self.assertEqual(item['status']['phase'], 'watching')
        self.assertIsNone(item['result'])
        self.assertEqual(item['process_liveness'], 'not_checked')
        self.assertTrue(report['recorded_anomalies'])
        (state_dir/'status.json').write_text('{broken')
        self.assertTrue(self.op('status', summary=True, terminal_id=[identity])['resources'][0]['errors'])

    def test_brief_ack_and_resources_keep_exact_checks_and_default_shape(self):
        self.publish('one')
        digest = hashlib.sha256((self.root/'one.txt').read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            self.op('ack', delivery_id='one', sha256='0'*64, disposition='done', brief=True)
        brief = self.op('ack', delivery_id='one', sha256=digest, disposition='done', brief=True)
        self.assertNotIn('terminals', brief)
        self.assertEqual(brief['pending'], 0)
        self.assertEqual(brief['state_sha256'], self.op('status', summary=True)['state_sha256'])
        self.assertIn('terminals', self.op('ack', delivery_id='one', sha256=digest, disposition='done'))
        identity = str(uuid.uuid4())
        self.assertEqual(self.op('terminal-add', terminal_id=identity, state_dir=self.root/'watch', brief=True)['unreconciled_terminals'], 1)

    def test_summary_retains_invalidations_without_reading_artifact(self):
        self.publish('bad')
        digest = hashlib.sha256((self.root/'bad.txt').read_bytes()).hexdigest()
        self.op('invalidate', delivery_id='bad', sha256=digest, reason='unusable', brief=True)
        (self.root/'bad.txt').unlink()
        report = self.op('status', summary=True)
        self.assertEqual(report['pending'], [])
        self.assertEqual(report['recorded_anomalies'][0]['delivery_id'], 'bad')
        with self.assertRaises(ValueError):
            self.op('ack', delivery_id='bad', sha256=digest, disposition='cannot accept')

    def test_rebind_preserves_ledger_and_is_idempotent_without_accepting_old_publisher(self):
        self.publish('old'); self.ack('old')
        before = self.op('status')
        args = self.handoff()
        first = self.op('rebind', **args)
        after = self.op('status')
        self.assertEqual(after['results'], before['results'])
        self.assertEqual(after['terminals'], before['terminals'])
        self.assertEqual(after['wake_history'], before['wake_history'])
        self.assertEqual(first, self.op('rebind', **args))
        self.assertEqual(first['rebind']['external_ownership'], 'operator_attested_not_host_verified')
        with self.assertRaises(ValueError): self.publish('late-old')
        self.publish('new', thread=args['new_thread'])
        self.assertIn('new', self.op('status')['results'])
        self.assertEqual(first['rebind'], self.op('rebind', **args)['rebind'])
        (args['handoff']).write_text((args['handoff']).read_text()+' ')
        with self.assertRaises(ValueError): self.op('rebind', **args)

    def test_rebind_rejects_stale_state_pending_wake_and_unreconciled_resources(self):
        args = self.handoff()
        self.publish('one')
        with self.assertRaises(ValueError): self.op('rebind', **args)
        args = self.handoff()
        with self.assertRaises(RuntimeError): self.op('rebind', **args)
        self.ack('one')
        identity = str(uuid.uuid4())
        self.op('terminal-add', terminal_id=identity, state_dir=self.root/'watch')
        with self.assertRaises(RuntimeError): self.op('rebind', **self.handoff())
        # No broad queue deletion or automatic retirement is attempted by rebind.
        with inbox.locked(self.mailbox) as root:
            state = inbox.load(root); state['terminals']={}; state['wake']={'status':'uncertain'}
            inbox.save_json(root/'state.json',state)
        with self.assertRaises(RuntimeError): self.op('rebind', **self.handoff())

    def test_rebind_requires_external_attestation_and_cannot_resume_or_reopen(self):
        with self.assertRaises(ValueError): self.op('rebind', **self.handoff(publishers_drained=False))
        with self.assertRaises(ValueError): self.op('rebind', **self.handoff(evidence=[]))
        self.op('pause')
        with self.assertRaises(RuntimeError): self.op('rebind', **self.handoff())
        self.op('resume'); self.op('close')
        with self.assertRaises(RuntimeError): self.op('rebind', **self.handoff())
        self.assertEqual(self.op('status')['mode'], 'closed')

    def test_rebind_save_failure_leaves_original_route_and_retry_can_complete(self):
        args = self.handoff(); before=(self.mailbox/'state.json').read_bytes()
        with patch.object(inbox, 'save_json', side_effect=OSError('disk full')):
            with self.assertRaises(OSError): self.op('rebind', **args)
        self.assertEqual((self.mailbox/'state.json').read_bytes(), before)
        self.assertEqual(self.op('rebind', **args)['thread'], args['new_thread'])


if __name__=='__main__':unittest.main(verbosity=2)
