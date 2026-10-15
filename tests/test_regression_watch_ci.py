"""Exercise CLI side effects with disposable gh/codex executables, never business threads."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
THREAD = '00000000-0000-4000-8000-000000000001'
SHA = 'a' * 40
STUB = '''#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
root=Path(__file__).resolve().parent.parent
name=Path(sys.argv[0]).name
with (root/(name+'-calls.jsonl')).open('a') as f:f.write(json.dumps(sys.argv[1:])+'\\n')
plan=json.loads((root/'plan.json').read_text())
if name=='codex':
 time.sleep(plan.get('queue_delay',0))
 (root/'accepted').touch()
 print('Queued message 00000000-0000-4000-8000-000000000002')
 sys.exit(plan.get('queue_exit',0))
countfile=root/'query-count'
count=int(countfile.read_text()) if countfile.exists() else 0
countfile.write_text(str(count+1))
responses=plan['responses'];value=responses[min(count,len(responses)-1)]
if value=='error':
 print('simulated API outage',file=sys.stderr);sys.exit(1)
if value=='malformed':print('{bad');sys.exit(0)
print(json.dumps(value))
'''


def github(status='completed', conclusion='success', **changes):
    return {'id': 17, 'run_attempt': 1, 'head_sha': SHA, 'status': status,
            'conclusion': conclusion, 'html_url': 'https://github.com/test/repo/actions/runs/17',
            'name': 'fixture', **changes}


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='watcher-unit-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        binaries = self.root / 'bin'
        binaries.mkdir()
        for name in ['gh', 'codex']:
            path = binaries / name
            path.write_text(STUB)
            path.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(binaries) + os.pathsep + os.environ['PATH']}
        self.state = self.root / 'state'
        self.plan([github()])

    def plan(self, responses, queue_exit=0, queue_delay=0):
        (self.root / 'plan.json').write_text(json.dumps({'responses': responses, 'queue_exit': queue_exit, 'queue_delay': queue_delay}))

    def calls(self, name):
        path = self.root / (name + '-calls.jsonl')
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def command(self, extra=()):
        return [sys.executable, str(SCRIPTS / 'watch_ci.py'), '--task', 'fixture',
                '--repo', 'test/repo', '--run-id', '17', '--attempt', '1', '--sha', SHA,
                '--thread', THREAD, '--state-dir', str(self.state), '--interval', '0.02',
                '--max-wait', '3', *extra]

    def watch(self, extra=()):
        return subprocess.run(self.command(extra), env=self.env, text=True, capture_output=True, timeout=8)

    def result(self):
        return json.loads((self.state / 'result.json').read_text())

    def test_pending_then_success_persists_before_notification(self):
        self.plan([github('in_progress', None), github()])
        self.assertEqual(self.watch().returncode, 0)
        self.assertEqual(len(self.calls('gh')), 2)
        self.assertEqual(self.result()['last_run']['conclusion'], 'success')
        self.assertEqual(len(self.calls('codex')), 1)
        message = self.calls('codex')[0][4]
        self.assertIn(str(self.state / 'result.json'), message)
        self.assertIn('artifact_sha256', message)

    def test_failure_and_remote_cancellation_both_notify(self):
        for conclusion in ['failure', 'cancelled']:
            with self.subTest(conclusion=conclusion):
                self.state = self.root / conclusion
                self.plan([github(conclusion=conclusion)])
                self.assertEqual(self.watch().returncode, 0)
                self.assertEqual(self.result()['outcome'], 'completed')
                self.assertEqual(self.result()['last_run']['conclusion'], conclusion)
        self.assertEqual(len(self.calls('codex')), 2)

    def test_new_attempt_and_other_sha_are_not_accepted_as_current(self):
        for key, value in [('run_attempt', 2), ('head_sha', 'b' * 40)]:
            with self.subTest(field=key):
                self.state = self.root / key
                self.plan([github(**{key: value})])
                self.assertEqual(self.watch().returncode, 0)
                self.assertEqual(self.result()['outcome'], 'superseded')
                self.assertFalse((self.state / 'ready.json').exists())

    def test_query_errors_and_invalid_json_are_monitor_failures(self):
        for response in ['error', 'malformed', github(id=99)]:
            with self.subTest(response=response):
                self.state = self.root / ('error-' + str(len(self.calls('codex'))))
                self.plan([response])
                self.assertEqual(self.watch().returncode, 0)
                self.assertEqual(self.result()['outcome'], 'monitor_error')
        self.assertEqual(len(self.calls('gh')), 9)
        self.assertEqual(len(self.calls('codex')), 3)

    def test_transient_error_recovers_without_false_failure(self):
        self.plan(['error', github('in_progress', None), github()])
        self.assertEqual(self.watch().returncode, 0)
        self.assertEqual(self.result()['outcome'], 'completed')
        self.assertEqual(len(self.calls('codex')), 1)

    def test_pending_run_reaches_finite_deadline_and_notifies(self):
        self.plan([github('in_progress', None)])
        self.assertEqual(self.watch(['--max-wait', '0.12']).returncode, 0)
        self.assertEqual(self.result()['outcome'], 'deadline')
        self.assertEqual(len(self.calls('codex')), 1)

    def test_explicit_stop_suppresses_notification(self):
        self.state.mkdir()
        (self.state / 'STOP').touch()
        self.assertEqual(self.watch().returncode, 0)
        self.assertEqual(self.result()['outcome'], 'stopped')
        self.assertEqual(self.calls('codex'), [])
        self.assertEqual(self.calls('gh'), [])

    def test_sigterm_stops_running_observer_without_callback(self):
        self.plan([github('in_progress', None)])
        process = subprocess.Popen(self.command(), env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 4
            while not (self.state / 'ready.json').exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue((self.state / 'ready.json').exists())
            process.send_signal(signal.SIGTERM)
            process.communicate(timeout=3)
            self.assertEqual(self.result()['outcome'], 'stopped')
            self.assertEqual(self.calls('codex'), [])
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_existing_observer_does_not_query_or_send_again(self):
        self.assertEqual(self.watch().returncode, 0)
        self.assertEqual(self.watch().returncode, 2)
        self.assertEqual(len(self.calls('gh')), 1)
        self.assertEqual(len(self.calls('codex')), 1)

    def test_resumed_observer_uses_a_new_delivery_identity(self):
        self.plan([github('in_progress', None)])
        self.assertEqual(self.watch(['--max-wait', '0.12']).returncode, 0)
        first = self.result()['observer_id']
        self.state = self.root / 'resumed'
        self.plan([github()])
        self.assertEqual(self.watch().returncode, 0)
        self.assertNotEqual(first, self.result()['observer_id'])
        messages = [entry[4] for entry in self.calls('codex')]
        self.assertIn(first, messages[0])
        self.assertNotIn(first, messages[1])

    def test_signal_during_queue_preserves_uncertainty_and_stops_cli(self):
        self.plan([github()], queue_delay=5)
        process = subprocess.Popen(self.command(), env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 4
            while not self.calls('codex') and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertEqual(len(self.calls('codex')), 1)
            process.send_signal(signal.SIGTERM)
            process.communicate(timeout=3)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads((self.state / 'status.json').read_text())['phase'], 'notification_uncertain')
            receipts = list((self.state / 'outbox').glob('*.receipt.json'))
            self.assertEqual(json.loads(receipts[0].read_text())['status'], 'uncertain')
            self.assertFalse((self.root / 'accepted').exists())
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_stop_file_during_queue_preserves_uncertainty_and_stops_cli(self):
        self.plan([github()], queue_delay=5)
        process = subprocess.Popen(self.command(), env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 4
            while not self.calls('codex') and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertEqual(len(self.calls('codex')), 1)
            (self.state / 'STOP').touch()
            process.communicate(timeout=3)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads((self.state / 'status.json').read_text())['phase'], 'notification_uncertain')
            receipts = list((self.state / 'outbox').glob('*.receipt.json'))
            self.assertEqual(json.loads(receipts[0].read_text())['status'], 'uncertain')
            self.assertFalse((self.root / 'accepted').exists())
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def queue_command(self):
        artifact = self.root / 'review.md'
        artifact.write_text('Independent result.\n')
        return [sys.executable, str(SCRIPTS / 'queue_result.py'), '--task', 'fixture',
                '--delivery-id', 'review-1', '--sender', 'reviewer', '--thread', THREAD,
                '--artifact', str(artifact), '--version', SHA, '--outbox', str(self.root / 'outbox'),
                '--summary', 'Literal `touch unexpected` and $(touch unexpected)']

    def test_accepted_replay_is_local_and_changed_payload_is_rejected(self):
        command = self.queue_command()
        for _ in range(2):
            self.assertEqual(subprocess.run(command, env=self.env, capture_output=True).returncode, 0)
        self.assertEqual(len(self.calls('codex')), 1)
        (self.root / 'review.md').write_text('Changed evidence')
        self.assertEqual(subprocess.run(command, env=self.env, capture_output=True).returncode, 2)
        self.assertEqual(len(self.calls('codex')), 1)
        self.assertFalse((self.root / 'unexpected').exists())

    def test_uncertain_and_missing_receipt_do_not_auto_retry(self):
        self.plan([github()], queue_exit=1)
        command = self.queue_command()
        for _ in range(2):
            self.assertEqual(subprocess.run(command, env=self.env, capture_output=True).returncode, 2)
        receipt = self.root / 'outbox/review-1.receipt.json'
        receipt.unlink()
        self.assertEqual(subprocess.run(command, env=self.env, capture_output=True).returncode, 2)
        self.assertEqual(len(self.calls('codex')), 1)

    def test_watcher_records_uncertain_notification_separately(self):
        self.plan([github()], queue_exit=1)
        self.assertEqual(self.watch().returncode, 2)
        self.assertEqual(self.result()['outcome'], 'completed')
        self.assertEqual(json.loads((self.state / 'status.json').read_text())['phase'], 'notification_uncertain')


if __name__ == '__main__':
    unittest.main(verbosity=2)
