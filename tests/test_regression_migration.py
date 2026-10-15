"""Exercise durable records and observer paths without a live agent or Android device."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import task_card
import task_inbox
from queue_result import deliver


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gallery-delivery-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mailbox = self.root / 'inbox'
        task_inbox.initialize(self.mailbox, 'fixture', transport='harness')

    def publish(self, identity='review-1', body='Review of the assigned candidate.'):
        artifact = self.root / (identity + '.md')
        artifact.write_text(body)
        return deliver(task='fixture', delivery_id=identity, sender='reviewer', artifact=artifact,
                       version='a' * 40, summary='done', outbox=self.root / 'outbox', mailbox=self.mailbox)

    def op(self, action, **kwargs):
        return task_inbox.operate(self.mailbox, action, **kwargs)

    def test_task_card_replacement_preserves_history_and_limits_current_state(self):
        task = self.root / 'task.md'
        history = '# History\n\nOriginal failure and its evidence.\n'
        task.write_text(history)
        task_card.write(task, 'Status: active\nGoal: first candidate\n')
        task_card.write(task, 'Status: paused\nNext: wait for maintainer\n')
        actual = task.read_text()
        self.assertTrue(actual.endswith(history))
        self.assertNotIn('first candidate', actual)
        self.assertEqual(actual.count(task_card.START), 1)
        self.assertIn('Updated:', task_card.card_of(actual))
        with self.assertRaises(ValueError):
            task_card.write(task, 'Status: active\n' + '\n'.join('Field: value' for _ in range(20)))
        self.assertEqual(task.read_text(), actual)

    def test_harness_publishes_without_node_or_codex_and_closes_after_ack(self):
        self.op('wait')
        with patch.object(task_inbox, 'submit', side_effect=AssertionError('harness must not queue')):
            receipt = self.publish()
        self.assertEqual(receipt['status'], 'recorded')
        self.assertIsNone(receipt['wake_status'])
        result = self.op('take')['results'][0]['payload']
        self.op('ack', delivery_id=result['delivery_id'], sha256=result['artifact_sha256'], disposition='reviewed')
        self.assertEqual(self.op('close')['mode'], 'closed')

    def test_overwritten_evidence_is_invalidated_without_approving_correction(self):
        self.publish()
        old = self.op('status')['results']['review-1']['payload']['artifact_sha256']
        (self.root / 'review-1.md').write_text('Overwritten after publication')
        with self.assertRaises(ValueError):
            self.op('ack', delivery_id='review-1', sha256=old, disposition='pass')
        self.publish('review-2')
        self.op('invalidate', delivery_id='review-1', sha256=old, reason='bytes changed', superseded_by='review-2')
        self.assertEqual([r['payload']['delivery_id'] for r in self.op('take')['results']], ['review-2'])
        audit = task_card.inbox_findings(self.mailbox)
        self.assertEqual(audit['pending'], ['review-2'])
        self.assertEqual(audit['changed_artifacts'], [])
        with self.assertRaises(RuntimeError):
            self.op('close')

    def observer(self, script, *extra, env=None):
        state = self.root / (script + '-state')
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), '--task', 'fixture', '--mailbox', str(self.mailbox),
             '--state-dir', str(state), *extra], capture_output=True, text=True, env=env, timeout=15)
        return result, state

    def test_local_command_records_exit_and_log_in_harness_inbox(self):
        process, state = self.observer('watch_cmd.py', '--label', 'compile', '--cwd', str(self.root),
                                       '--', sys.executable, '-c', 'print("compiler failure"); raise SystemExit(7)')
        self.assertEqual(process.returncode, 0, process.stderr)
        observation = json.loads((state / 'result.json').read_text())
        self.assertEqual((observation['outcome'], observation['exit_code']), ('failed', 7))
        self.assertIn('compiler failure', observation['log_tail'])
        payload = self.op('take')['results'][0]['payload']
        self.assertEqual(payload['artifact_sha256'], hashlib.sha256((state / 'result.json').read_bytes()).hexdigest())

    def test_local_command_success_remains_distinct_from_failed_exit(self):
        process, state = self.observer('watch_cmd.py', '--label', 'compile', '--cwd', str(self.root),
                                       '--', sys.executable, '-c', 'print("compiled")')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads((state / 'result.json').read_text())['outcome'], 'succeeded')

    def test_command_deadline_reaps_its_owned_process_group(self):
        process, state = self.observer('watch_cmd.py', '--label', 'ordinary-test', '--cwd', str(self.root),
                                       '--max-wait', '0.1', '--', sys.executable, '-c', 'import time; time.sleep(30)')
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads((state / 'result.json').read_text())
        self.assertEqual(result['outcome'], 'deadline')
        child = json.loads((state / 'ready.json').read_text())['child_pid']
        with self.assertRaises(ProcessLookupError):
            os.kill(child, 0)

    def test_recorded_expected_result_does_not_publish_another_notification(self):
        self.publish()
        process, state = self.observer('watch_result.py', '--expect', 'review-1', '--version', 'a' * 40,
                                       '--interval', '0.01', '--max-wait', '1')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads((state / 'result.json').read_text())['outcome'], 'arrived')
        self.assertEqual(len(self.op('take')['results']), 1)

    def test_overdue_observer_reports_without_running_a_worker(self):
        process, state = self.observer('watch_result.py', '--expect', 'missing-1', '--version', 'a' * 40,
                                       '--interval', '0.01', '--max-wait', '0.1')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads((state / 'result.json').read_text())['outcome'], 'overdue')
        self.assertEqual(len(self.op('take')['results']), 1)

    def test_observer_rejects_wrong_task_before_command_can_run(self):
        marker = self.root / 'executed'
        process, state = self.observer('watch_cmd.py', '--task', 'other-task', '--label', 'bad-target',
                                       '--', sys.executable, '-c', f'from pathlib import Path; Path({str(marker)!r}).touch()')
        self.assertNotEqual(process.returncode, 0)
        self.assertFalse(marker.exists())
        self.assertFalse((state / 'ready.json').exists())


if __name__ == '__main__':
    unittest.main()
