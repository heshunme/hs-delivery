"""Command diagnostics retain evidence and never manufacture clean source or process state."""

import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import task_inbox
import watch_cmd


class CommandObservationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='hs-command-')
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_failed_git_status_is_unknown_instead_of_clean(self):
        replies = [SimpleNamespace(returncode=0, stdout='a' * 40 + '\n'),
                   SimpleNamespace(returncode=128, stdout='')]
        with patch('watch_cmd.subprocess.run', side_effect=replies):
            result = watch_cmd.source_identity(self.root)
        self.assertIsNone(result['dirty'])
        self.assertIn('unknown', result['version'])
        self.assertIn('git status failed', result['error'])

    def test_failure_before_log_tail_is_located_and_original_preserved(self):
        log = self.root / 'build.log'
        original = 'ERROR missing model at startup\n' + 'cleanup completed\n' * 100
        log.write_text(original)
        result = watch_cmd.diagnostics(log)
        self.assertEqual(result['matches'][0]['line'], 1)
        self.assertIn('missing model', result['matches'][0]['text'])
        self.assertNotIn('missing model', '\n'.join(watch_cmd.tail(log)))
        self.assertTrue(result['scan_complete'])
        self.assertEqual(log.read_text(), original)

    def test_bounded_scan_and_missing_log_do_not_claim_full_inspection(self):
        log = self.root / 'build.log'
        log.write_text('ordinary output\n' * 100 + 'ERROR late failure\n')
        result = watch_cmd.diagnostics(log, max_bytes=100)
        self.assertFalse(result['scan_complete'])
        self.assertEqual(result['bytes_scanned'], 100)
        self.assertEqual(result['matches'], [])
        log.unlink()
        missing = watch_cmd.diagnostics(log)
        self.assertFalse(missing['scan_complete'])
        self.assertIn('error', missing)

    def test_long_matching_line_has_bounded_excerpt(self):
        log = self.root / 'large.log'
        log.write_text('prefix ' * 500 + ' ERROR ' + 'detail ' * 20000)
        result = watch_cmd.diagnostics(log)
        self.assertIn('ERROR', result['matches'][0]['text'])
        self.assertTrue(result['matches'][0]['truncated'])
        self.assertLessEqual(len(result['matches'][0]['text']), 1000)

    def test_readiness_failure_reaps_the_launched_child(self):
        state = self.root / 'state'
        state.mkdir()
        args = SimpleNamespace(command=[sys.executable, '-c', 'import time; time.sleep(120)'],
                               cwd=str(self.root), max_wait=10)
        launched = []
        popen = subprocess.Popen

        def capture(*args, **kwargs):
            child = popen(*args, **kwargs)
            launched.append(child)
            return child

        with patch('watch_cmd.subprocess.Popen', side_effect=capture), \
                patch('watch_cmd.save_json', side_effect=OSError('readiness disk failure')):
            with self.assertRaisesRegex(OSError, 'readiness disk failure'):
                watch_cmd.run(args, state, threading.Event(), state / 'command.log')
        self.assertEqual(len(launched), 1)
        self.assertIsNotNone(launched[0].poll())

    @unittest.skipUnless(sys.platform == 'linux', 'uses /proc to distinguish a killed zombie from a running descendant')
    def test_stop_reaps_leader_and_kills_descendant_ignoring_term(self):
        ready = self.root / 'descendant.pid'
        program = '\n'.join([
            'import os, pathlib, signal, sys, time',
            'pid = os.fork()',
            'if pid == 0:',
            '    signal.signal(signal.SIGTERM, signal.SIG_IGN)',
            '    pathlib.Path(sys.argv[1]).write_text(str(os.getpid()))',
            '    time.sleep(120)',
            'else:',
            '    time.sleep(120)',
        ])
        child = subprocess.Popen([sys.executable, '-c', program, str(ready)],
                                 start_new_session=True)
        self.addCleanup(lambda: watch_cmd.kill_group(child, signal.SIGKILL))
        self.addCleanup(lambda: child.poll())
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(ready.exists(), 'descendant did not start')
        descendant = int(ready.read_text())
        watch_cmd.stop_child(child)
        self.assertIsNotNone(child.returncode)
        status = Path(f'/proc/{descendant}/stat')
        deadline = time.monotonic() + 2
        running = True
        while running and time.monotonic() < deadline:
            try:
                running = status.read_text().split(') ', 1)[1].split()[0] not in ('Z', 'X')
            except FileNotFoundError:
                running = False
            if running:
                time.sleep(0.01)
        self.assertFalse(running, 'descendant still running after group cleanup')

    def test_cli_publishes_exit_with_early_failure_and_full_log(self):
        inbox = self.root / 'inbox'
        task_inbox.initialize(inbox, 'command-fixture', transport='harness')
        state = self.root / 'observer'
        command = [sys.executable, str(SCRIPTS / 'watch_cmd.py'),
                   '--task', 'command-fixture', '--label', 'failure', '--cwd', str(self.root),
                   '--state-dir', str(state), '--mailbox', str(inbox), '--max-wait', '10',
                   '--', sys.executable, '-c',
                   'print("ERROR original cause"); print("cleanup\\n" * 100); raise SystemExit(7)']
        completed = subprocess.run(command, capture_output=True, text=True, timeout=15)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads((state / 'result.json').read_text())
        self.assertEqual((result['outcome'], result['exit_code']), ('failed', 7))
        self.assertIn('original cause', result['diagnostics']['matches'][0]['text'])
        self.assertIn('original cause', Path(result['log']).read_text())
        self.assertEqual(len(task_inbox.operate(inbox, 'take')['results']), 1)


if __name__ == '__main__':
    unittest.main()
