"""Exercise portable records and local result delivery without contacting a live host."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import task_card
import task_inbox
import watch_cmd
from queue_result import deliver


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hs-delivery-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = self.root / 'task'
        self.task.mkdir()
        self.mailbox = self.task / 'inbox'

    def command(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, args)],
            cwd=self.root, capture_output=True, text=True, timeout=15,
        )

    def inbox(self):
        return task_inbox.initialize(self.mailbox, 'fixture')

    def publish(self, identity='review.r1', text='Reviewed candidate A'):
        artifact = self.task / f'{identity}.md'
        artifact.write_text(text)
        receipt = deliver(
            task='fixture', delivery_id=identity, sender='reviewer', artifact=artifact,
            version='candidate-A', summary='review complete', outbox=self.task / 'outbox',
            mailbox=self.mailbox,
        )
        return artifact, receipt

    def test_card_replacement_preserves_history_and_rejects_oversized_card(self):
        path = self.task / 'task.md'
        history = '# History\n\nOriginal failure and version.\n'
        path.write_text(history)
        task_card.write(path, 'Status: active\nNext: inspect candidate\n')
        task_card.write(path, 'Status: closed\nNext: none\n')
        self.assertEqual(path.read_text().count(task_card.START), 1)
        self.assertTrue(path.read_text().endswith(history))
        self.assertEqual(task_card.field(task_card.card_of(path.read_text()), 'Status'), 'closed')
        previous = path.read_bytes()
        with self.assertRaises(ValueError):
            task_card.write(path, 'Status: active\n' + '\n'.join('Extra: value' for _ in range(20)))
        self.assertEqual(path.read_bytes(), previous)

    def test_card_audits_explicit_target_repo_from_unrelated_directory(self):
        repo = self.root / 'different-project'
        subprocess.run(['git', 'init', '-q', str(repo)], check=True, capture_output=True)
        result = self.command('task_card.py', 'check', '--task-dir', self.task, '--repo', repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['linked_worktrees'], [])
        missing_repo = self.command('task_card.py', 'check', '--task-dir', self.task)
        self.assertEqual(missing_repo.returncode, 2)

    def test_card_audit_reports_an_invalid_repository_as_an_error(self):
        repo = self.root / 'missing-repository'
        result = self.command('task_card.py', 'check', '--task-dir', self.task, '--repo', repo)
        self.assertEqual(result.returncode, 2)
        self.assertIn(str(repo), result.stderr)
        self.assertIn('worktree', result.stderr)

    def test_worktree_audit_distinguishes_clean_dirty_and_unreadable_checkouts(self):
        repo = self.root / 'repository'
        subprocess.run(['git', 'init', '-q', str(repo)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '-q',
                        '--allow-empty', '-m', 'fixture'], check=True, capture_output=True)
        linked = self.root / 'linked-checkout'
        subprocess.run(['git', '-C', str(repo), 'worktree', 'add', '-q', '-b',
                        'fixture-linked', str(linked)], check=True, capture_output=True)
        self.assertIs(task_card.worktrees(repo)[0]['dirty'], False)
        (linked / 'untracked.txt').write_text('local input')
        self.assertIs(task_card.worktrees(repo)[0]['dirty'], True)
        shutil.rmtree(linked)
        record = task_card.worktrees(repo)[0]
        self.assertIsNone(record['dirty'])
        self.assertTrue(record['prunable'])
        self.assertTrue(record['error'])

    def test_stop_already_requested_prevents_command_launch_and_log_creation(self):
        for mechanism in ['file', 'signal']:
            with self.subTest(mechanism=mechanism):
                state = self.task / f'stopped-before-launch-{mechanism}'
                state.mkdir()
                stopped = threading.Event()
                if mechanism == 'file':
                    (state / 'STOP').touch()
                else:
                    stopped.set()
                args = SimpleNamespace(command=['must-not-launch'], cwd=str(self.root), max_wait=10)
                log = state / 'command.log'
                with patch('watch_cmd.subprocess.Popen', side_effect=AssertionError('command launched after stop')):
                    result = watch_cmd.run(args, state, stopped, log)
                self.assertEqual(result['outcome'], 'stopped')
                self.assertIsNone(result['exit_code'])
                self.assertFalse(log.exists())
                self.assertFalse((state / 'ready.json').exists())

    def test_default_inbox_and_waiting_publication_never_send_a_queue_message(self):
        with patch('task_inbox.submit', side_effect=AssertionError('unexpected external send')):
            state = self.inbox()
            self.assertEqual(state['transport'], 'harness')
            self.assertEqual(task_inbox.operate(self.mailbox, 'wait')['mode'], 'waiting')
            _, receipt = self.publish()
        self.assertEqual(receipt['status'], 'recorded')
        self.assertIsNone(task_inbox.operate(self.mailbox, 'status')['wake'])
        self.assertEqual(len(task_inbox.operate(self.mailbox, 'take')['results']), 1)

    def test_harness_needs_no_site_packages_and_queue_reports_missing_dependency(self):
        program = '\n'.join([
            'import sys',
            'sys.path.insert(0, sys.argv[1])',
            'from task_inbox import initialize',
            'from queue_control import QueueControl',
            'assert initialize(sys.argv[2], "fixture")["transport"] == "harness"',
            'try:',
            '    QueueControl("unix:///unused-fixture.sock")',
            'except RuntimeError as error:',
            '    assert "Queue transport requires" in str(error)',
            'else:',
            '    raise AssertionError("queue dependency was not checked")',
        ])
        result = subprocess.run(
            [sys.executable, '-S', '-c', program, str(SCRIPTS), str(self.mailbox)],
            cwd=self.root, capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_result_replay_is_idempotent_but_changed_payload_is_rejected(self):
        self.inbox()
        self.publish()
        _, replay = self.publish()
        self.assertEqual(replay['status'], 'recorded')
        self.assertEqual(len(task_inbox.operate(self.mailbox, 'take')['results']), 1)
        with self.assertRaises(RuntimeError):
            self.publish(text='A different claim under the same ID')

    def test_close_requires_disposition_and_ack_rejects_changed_artifact(self):
        self.inbox()
        artifact, _ = self.publish()
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        with self.assertRaises(RuntimeError):
            task_inbox.operate(self.mailbox, 'close')
        artifact.write_text('Overwritten evidence')
        with self.assertRaises(ValueError):
            task_inbox.operate(self.mailbox, 'ack', delivery_id='review.r1', sha256=digest,
                               disposition='reviewed')
        self.assertEqual(task_card.inbox_findings(self.mailbox)['changed_artifacts'], ['review.r1'])

    def test_invalidated_evidence_does_not_approve_its_correction(self):
        self.inbox()
        artifact, _ = self.publish()
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        artifact.unlink()
        correction, _ = self.publish('review.r2', 'Retest on candidate B')
        task_inbox.operate(self.mailbox, 'invalidate', delivery_id='review.r1', sha256=digest,
                           reason='original artifact lost', superseded_by='review.r2')
        remaining = task_inbox.operate(self.mailbox, 'take')['results']
        self.assertEqual([entry['payload']['delivery_id'] for entry in remaining], ['review.r2'])
        task_inbox.operate(self.mailbox, 'ack', delivery_id='review.r2',
                           sha256=hashlib.sha256(correction.read_bytes()).hexdigest(),
                           disposition='correction independently checked')
        self.assertEqual(task_inbox.operate(self.mailbox, 'close')['mode'], 'closed')
        with self.assertRaises(RuntimeError):
            self.publish('late-result')

    def test_pause_requires_explicit_resume_but_keeps_arriving_results(self):
        self.inbox()
        task_inbox.operate(self.mailbox, 'pause')
        self.publish()
        with self.assertRaises(RuntimeError):
            task_inbox.operate(self.mailbox, 'take')
        task_inbox.operate(self.mailbox, 'resume')
        self.assertEqual(len(task_inbox.operate(self.mailbox, 'take')['results']), 1)

    def test_command_observer_records_failure_and_refuses_reused_binding(self):
        self.inbox()
        state = self.task / 'command-observer'
        result = self.command(
            'watch_cmd.py', '--task', 'fixture', '--label', 'fixture-command',
            '--cwd', self.root, '--state-dir', state, '--mailbox', self.mailbox,
            '--max-wait', '10', '--', sys.executable, '-c',
            'print("expected diagnostic"); raise SystemExit(7)',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        observation = json.loads((state / 'result.json').read_text())
        self.assertEqual((observation['outcome'], observation['exit_code']), ('failed', 7))
        self.assertIn('expected diagnostic', '\n'.join(observation['log_tail']))
        self.assertEqual(json.loads((state / 'status.json').read_text())['phase'], 'recorded')
        marker = self.root / 'must-not-run'
        repeated = self.command(
            'watch_cmd.py', '--task', 'fixture', '--label', 'fixture-command',
            '--cwd', self.root, '--state-dir', state, '--mailbox', self.mailbox,
            '--max-wait', '10', '--', sys.executable, '-c',
            f'from pathlib import Path; Path({str(marker)!r}).touch()',
        )
        self.assertEqual(repeated.returncode, 2)
        self.assertFalse(marker.exists())

    def test_ci_stop_suppresses_query_and_publication(self):
        self.inbox()
        state = self.task / 'ci-observer'
        state.mkdir()
        (state / 'STOP').touch()
        result = self.command(
            'watch_ci.py', '--task', 'fixture', '--repo', 'fixture/project',
            '--run-id', '1', '--attempt', '1', '--sha', 'a' * 40,
            '--state-dir', state, '--mailbox', self.mailbox,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((state / 'status.json').read_text())['phase'], 'stopped')
        self.assertEqual(task_inbox.operate(self.mailbox, 'take')['results'], [])

    def test_expected_result_exits_without_publishing_a_duplicate_notice(self):
        self.inbox()
        self.publish()
        state = self.task / 'expected-observer'
        result = self.command(
            'watch_result.py', '--task', 'fixture', '--expect', 'review.r1',
            '--version', 'candidate-A', '--max-wait', '10',
            '--state-dir', state, '--mailbox', self.mailbox,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((state / 'result.json').read_text())['outcome'], 'arrived')
        self.assertEqual(len(task_inbox.operate(self.mailbox, 'take')['results']), 1)


if __name__ == '__main__':
    unittest.main()
