"""Daily verification must inspect explicit inputs without substituting for closeout."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import task_card


class CurrentScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='delivery-current-scope-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = self.root / 'task'
        self.task.mkdir()
        task_card.write(self.task / 'task.md', 'Status: active\nNext: reconcile selected result\n')
        self.inbox = self.task / 'inbox'
        self.inbox.mkdir()
        (self.inbox / 'lock').touch()
        self.state = {'task': 'fixture', 'mode': 'waiting', 'results': {}, 'terminals': {}}
        self.save_state()

    def save_state(self):
        (self.inbox / 'state.json').write_text(json.dumps(self.state))

    def result(self, identity, *, disposed=False, invalidated=False):
        artifact = self.task / (identity + '.md')
        artifact.write_text('Result for ' + identity)
        entry = {'payload': {'artifact': str(artifact),
                             'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}}
        if disposed:
            entry['disposition'] = 'reviewed on its recorded inputs'
        if invalidated:
            entry['invalidation'] = {'reason': 'superseded evidence'}
        self.state['results'][identity] = entry
        self.save_state()
        return artifact

    def command(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / 'task_card.py'), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True, timeout=15)

    def git(self, directory, *args):
        return subprocess.run(['git', '-C', str(directory), *args], check=True,
                              capture_output=True, text=True, timeout=15).stdout.strip()

    def repository(self, name='repo'):
        repo = self.root / name
        repo.mkdir()
        self.git(repo, 'init', '-q')
        self.git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-q', '--allow-empty', '-m', 'fixture')
        return repo

    def test_pending_scope_hashes_only_pending_in_named_inbox_and_does_not_mutate_it(self):
        historical = self.result('old', disposed=True)
        historical.write_text('changed after disposition')
        current = self.result('current')
        # A broken unrelated inbox must not be discovered by the daily path.
        unrelated = self.task / 'old-run' / 'inbox'
        unrelated.mkdir(parents=True)
        (unrelated / 'state.json').write_text('not json')
        (unrelated / 'lock').touch()
        self.state['terminals']['old-observer'] = {'status': 'running'}
        self.save_state()
        before = (self.inbox / 'state.json').read_bytes()
        with patch.object(task_card, 'current_artifact', wraps=task_card.current_artifact) as read:
            report = task_card.check_current(self.task, inbox=self.inbox, pending_results=True)
        self.assertEqual(report['outcome'], 'checked')
        self.assertEqual([call.args[0] for call in read.call_args_list], [current])
        selected = report['checked']['inbox']
        self.assertEqual(set(selected['results']), {'current'})
        self.assertEqual(selected['unselected_result_count'], 1)
        self.assertTrue(selected['results']['current']['pending'])
        self.assertTrue(any('Terminal' in scope for scope in report['not_checked']))
        self.assertEqual((self.inbox / 'state.json').read_bytes(), before)
        self.assertEqual(task_card.inbox_findings(self.inbox)['changed_artifacts'], ['old'])

    def test_exact_selection_includes_disposed_artifact_and_unknown_id(self):
        old = self.result('old', disposed=True)
        old.unlink()
        self.result('unselected')
        result = self.command('check-current', '--task-dir', self.task, '--inbox', self.inbox,
                              '--result-id', 'old', '--result-id', 'missing')
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['outcome'], 'attention')
        selected = report['checked']['inbox']['results']
        self.assertEqual(set(selected), {'old', 'missing'})
        self.assertEqual(selected['old']['status'], 'unknown')
        self.assertEqual(selected['missing']['status'], 'unknown')
        self.assertEqual({issue['identity'] for issue in report['issues']}, {'old', 'missing'})

    def test_bad_hash_and_invalidated_result_are_not_reported_as_verified(self):
        changed = self.result('changed')
        changed.write_text('different bytes')
        self.result('invalidated', invalidated=True)
        report = task_card.check_current(self.task, inbox=self.inbox, pending_results=True)
        self.assertEqual(report['outcome'], 'attention')
        selected = report['checked']['inbox']['results']
        self.assertEqual(selected['changed']['status'], 'changed')
        self.assertEqual(selected['invalidated']['status'], 'matched')
        self.assertTrue(selected['invalidated']['invalidated'])
        self.assertEqual({issue['identity'] for issue in report['issues']}, {'changed', 'invalidated'})

    def test_explicit_candidate_files_require_valid_hash_and_readable_bytes(self):
        candidate = self.task / 'candidate.patch'
        candidate.write_bytes(b'candidate input\x00\xff')
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        result = self.command('check-current', '--task-dir', self.task,
                              '--artifact', candidate, digest.upper())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['checked']['artifacts'][0]['status'], 'matched')
        for path, expected, status in [(candidate, '0' * 64, 'changed'),
                                       (candidate, 'not-a-digest', 'unknown'),
                                       (self.task / 'gone', digest, 'unknown')]:
            with self.subTest(path=path, expected=expected):
                result = self.command('check-current', '--task-dir', self.task,
                                      '--artifact', path, expected)
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['checked']['artifacts'][0]['status'], status)
                self.assertTrue(report['issues'])

    def test_selected_checkout_reports_current_identity_without_visiting_other_worktrees(self):
        repo = self.repository()
        selected = self.root / 'selected-owner'
        unavailable = self.root / 'historical-checkout'
        self.git(repo, 'worktree', 'add', '-q', '-b', 'selected', str(selected))
        self.git(repo, 'worktree', 'add', '-q', '-b', 'historical', str(unavailable))
        shutil.rmtree(unavailable)
        (selected / 'candidate.txt').write_text('uncommitted input')
        head = self.git(selected, 'rev-parse', 'HEAD')
        index = Path(self.git(selected, 'rev-parse', '--git-path', 'index'))
        before = index.read_bytes()
        with patch.object(task_card, 'worktrees', side_effect=AssertionError('full audit was called')):
            report = task_card.check_current(self.task, repo=repo,
                                            selected_worktrees=[selected, selected])
        self.assertEqual(report['outcome'], 'checked')
        self.assertEqual(len(report['checked']['worktrees']), 1)
        actual = report['checked']['worktrees'][0]
        self.assertEqual(actual['head'], head)
        self.assertIs(actual['dirty'], True)
        self.assertEqual(index.read_bytes(), before)
        self.assertTrue(any('candidate pin' in scope for scope in report['not_checked']))
        # The existing complete audit still discovers the unavailable historical checkout.
        full = task_card.check(self.task, repo)
        missing = next(row for row in full['linked_worktrees'] if row['path'] == str(unavailable))
        self.assertIsNone(missing['dirty'])
        self.assertTrue(missing['error'])

    def test_unrelated_unreadable_or_nonroot_checkout_cannot_satisfy_scope(self):
        repo = self.repository()
        other = self.repository('other')
        nested = repo / 'nested'
        nested.mkdir()
        for selected in [other, nested, self.root / 'missing']:
            with self.subTest(selected=selected):
                result = self.command('check-current', '--task-dir', self.task, '--repo', repo,
                                      '--worktree', selected)
                self.assertEqual(result.returncode, 1, result.stderr)
                row = json.loads(result.stdout)['checked']['worktrees'][0]
                self.assertEqual(row['status'], 'unknown')
                self.assertIsNone(row['dirty'])
                self.assertTrue(row['error'])

    def test_hidden_untracked_setting_does_not_make_candidate_look_clean(self):
        repo = self.repository()
        selected = self.root / 'owner'
        self.git(repo, 'worktree', 'add', '-q', '-b', 'owner', str(selected))
        self.git(repo, 'config', 'status.showUntrackedFiles', 'no')
        (selected / 'new-input.txt').write_text('candidate input not yet committed')
        report = task_card.check_current(self.task, repo=repo, selected_worktrees=[selected])
        self.assertIs(report['checked']['worktrees'][0]['dirty'], True)
        full = task_card.check(self.task, repo)
        self.assertIs(full['linked_worktrees'][0]['dirty'], True)

    def test_missing_card_and_malformed_selected_inbox_are_attention_not_success(self):
        (self.task / 'task.md').unlink()
        (self.inbox / 'state.json').write_text('broken')
        result = self.command('check-current', '--task-dir', self.task,
                              '--inbox', self.inbox, '--pending-results')
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual({issue['area'] for issue in report['issues']}, {'card', 'inbox'})

    def test_inconsistent_registration_or_result_identity_is_unknown(self):
        self.result('current')
        self.state['results']['current']['payload']['task'] = 'different-task'
        self.save_state()
        report = task_card.check_current(self.task, inbox=self.inbox, pending_results=True)
        self.assertEqual(report['checked']['inbox']['results']['current']['status'], 'unknown')
        self.assertEqual(report['outcome'], 'attention')
        self.state['results']['current']['payload'].pop('task')
        self.state['results']['current']['payload']['artifact'] = 'current.md'
        self.save_state()
        report = task_card.check_current(self.task, inbox=self.inbox, pending_results=True)
        self.assertEqual(report['checked']['inbox']['results']['current']['status'], 'unknown')
        (self.inbox / 'lock').unlink()
        report = task_card.check_current(self.task, inbox=self.inbox, pending_results=True)
        self.assertEqual(report['outcome'], 'attention')
        self.assertEqual(report['issues'][0]['area'], 'inbox')

    def test_scope_must_be_explicit_and_result_or_worktree_dependencies_are_required(self):
        for args in [[], ['--inbox', self.inbox], ['--pending-results'],
                     ['--result-id', 'unknown'], ['--worktree', self.root],
                     ['--inbox', self.inbox, '--pending-results', '--result-id', 'unknown']]:
            with self.subTest(args=args):
                result = self.command('check-current', '--task-dir', self.task, *args)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(result.stdout)

    def test_show_and_full_check_retain_the_existing_output_contract(self):
        repo = self.repository()
        changed = self.result('historical', disposed=True)
        changed.write_text('changed evidence')
        result = self.command('check', '--task-dir', self.task, '--repo', repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(set(report), {'task', 'card', 'inboxes', 'linked_worktrees'})
        self.assertEqual(report['inboxes']['inbox']['changed_artifacts'], ['historical'])
        result = self.command('show', '--task-dir', self.task)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), task_card.card_of((self.task / 'task.md').read_text()))


if __name__ == '__main__':
    unittest.main()
