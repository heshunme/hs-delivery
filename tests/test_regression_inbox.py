"""Exercise observable batching, races, cancellations and resource closeout locally."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import sys
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


if __name__=='__main__':unittest.main(verbosity=2)
