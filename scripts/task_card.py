#!/usr/bin/env python3
"""Keep a task's short current card at the top of task.md and audit what closeout still owes."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

START = '<!-- task-card:start -->'
END = '<!-- task-card:end -->'
STATUSES = ('active', 'paused', 'closed')
MAX_LINES = 20


def card_of(text):
    """Return the card body between the markers, or None when the file has no card."""
    match = re.search(re.escape(START) + r'\n(.*?)\n' + re.escape(END), text, re.S)
    return match[1] if match else None


def field(card, name):
    """Read one `Name: value` line from a card."""
    match = re.search(rf'^{re.escape(name)}:\s*(.*)$', card, re.M)
    return match[1].strip() if match else None


def write(task_md, card):
    """Replace the whole card in place, or put a new one above the first line; nothing else changes."""
    lines = [x for x in card.strip('\n').splitlines() if not x.startswith('Updated:')]
    status = field('\n'.join(lines), 'Status')
    if status not in STATUSES:
        raise ValueError(f'card needs a "Status:" line with one of {", ".join(STATUSES)}')
    stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    lines.insert(next(i for i, x in enumerate(lines) if x.startswith('Status:')) + 1, f'Updated: {stamp}')
    if len(lines) > MAX_LINES:
        raise ValueError(f'card has {len(lines)} lines; keep it to {MAX_LINES} and link details instead')
    block = START + '\n' + '\n'.join(lines) + '\n' + END
    text = task_md.read_text() if task_md.exists() else ''
    if card_of(text) is not None:
        start, end = text.index(START), text.index(END) + len(END)
        text = text[:start] + block + text[end:]
    else:
        text = block + '\n\n' + text
    temporary = task_md.with_name(task_md.name + f'.{os.getpid()}.tmp')
    temporary.write_text(text)
    temporary.replace(task_md)
    return block


def inbox_findings(inbox):
    """List results without a disposition, artifacts whose bytes changed, and owned terminals not reconciled."""
    state = json.loads((inbox / 'state.json').read_text())
    found = {'mode': state['mode'], 'pending': [], 'changed_artifacts': [], 'terminals': []}
    for identity, entry in state['results'].items():
        payload = entry['payload']
        if 'disposition' not in entry:
            found['pending'].append(identity)
        try:
            digest = hashlib.sha256(Path(payload['artifact']).read_bytes()).hexdigest()
        except OSError:
            digest = None
        if digest != payload['artifact_sha256'] and 'invalidation' not in entry:
            found['changed_artifacts'].append(identity)
    found['terminals'] = [k for k, v in state.get('terminals', {}).items() if v['status'] != 'removed']
    return found


def worktrees(repo):
    """Report every linked worktree, wherever its host created it, with its branch and dirty state."""
    result = subprocess.run(['git', '-C', str(repo), 'worktree', 'list', '--porcelain'],
                            text=True, capture_output=True, timeout=30)
    if result.returncode:
        detail = result.stderr.strip() or f'git exited {result.returncode}'
        raise RuntimeError(f'cannot inspect worktrees for {repo}: {detail}')
    entries = []
    # the first entry is the main checkout itself
    for chunk in result.stdout.strip().split('\n\n')[1:]:
        info = dict(line.split(' ', 1) for line in chunk.splitlines() if ' ' in line)
        path = info.get('worktree', '')
        if not path:
            continue
        status = subprocess.run(['git', '-C', path, 'status', '--porcelain', '--untracked-files=all'],
                                text=True, capture_output=True, timeout=30)
        entry = {'path': path, 'branch': info.get('branch'),
                 'dirty': None if status.returncode else bool(status.stdout.strip()),
                 'prunable': any(line.startswith('prunable') for line in chunk.splitlines())}
        if status.returncode:
            entry['error'] = status.stderr.strip() or f'git status exited {status.returncode}'
        entries.append(entry)
    return entries


def check(task_dir, repo):
    """Gather closeout debts read-only; never acknowledge, close or remove anything."""
    task_md = task_dir / 'task.md'
    card = card_of(task_md.read_text()) if task_md.exists() else None
    report = {'task': task_dir.name, 'card': None if card is None else {
        'status': field(card, 'Status'), 'updated': field(card, 'Updated'),
        'expecting': field(card, 'Expecting'), 'next': field(card, 'Next')}}
    inboxes = [p.parent for p in task_dir.glob('**/state.json') if (p.parent / 'lock').exists()]
    report['inboxes'] = {str(p.relative_to(task_dir)): inbox_findings(p) for p in sorted(inboxes)}
    report['linked_worktrees'] = worktrees(repo)
    return report


def current_artifact(path, expected):
    """Read one explicitly selected file; do not treat unreadable bytes as a matching hash."""
    record = {'path': str(path), 'expected_sha256': expected, 'status': 'unknown'}
    if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', expected):
        record['error'] = 'expected SHA-256 must contain 64 hexadecimal characters'
        return record
    try:
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
        record['actual_sha256'] = digest.hexdigest()
        record['status'] = 'matched' if digest.hexdigest() == expected.lower() else 'changed'
    except OSError as error:
        record['error'] = str(error)
    return record


def current_worktree(path, repo):
    """Inspect only an explicitly selected checkout in the given repository, without index refresh writes."""
    record = {'path': str(path), 'status': 'unknown', 'dirty': None}
    env = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}

    def git(directory, *args):
        result = subprocess.run(['git', '-C', str(directory), *args], text=True,
                                capture_output=True, timeout=30, env=env)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f'git exited {result.returncode}')
        return result.stdout.strip()

    def common(directory):
        location = Path(git(directory, 'rev-parse', '--git-common-dir'))
        return (directory / location).resolve() if not location.is_absolute() else location.resolve()

    try:
        # A directory inside another checkout is not a selected worktree root.
        top = Path(git(path, 'rev-parse', '--show-toplevel')).resolve()
        if top != path:
            raise ValueError(f'not a checkout root (root is {top})')
        if common(path) != common(repo):
            raise ValueError(f'checkout does not belong to repository {repo}')
        record['head'] = git(path, 'rev-parse', '--verify', 'HEAD')
        record['dirty'] = bool(git(path, 'status', '--porcelain', '--untracked-files=all'))
        record['status'] = 'inspected'
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        record['error'] = str(error)
    return record


def check_current(task_dir, *, inbox=None, pending_results=False, result_ids=(),
                  repo=None, selected_worktrees=(), artifacts=()):
    """Verify explicit daily inputs, never discover historical inboxes or inspect other checkouts.

    This is a bounded snapshot, not closeout or product acceptance. Result selection is either
    the pending entries in one named inbox or exact IDs. Checkout paths come from the caller's
    candidate/ownership record; HEAD is reported, not compared with a guessed candidate pin.
    """
    if pending_results and result_ids:
        raise ValueError('choose --pending-results or --result-id, not both')
    if (pending_results or result_ids) and inbox is None:
        raise ValueError('result selection requires --inbox')
    if inbox is not None and not (pending_results or result_ids):
        raise ValueError('--inbox requires --pending-results or --result-id')
    if selected_worktrees and repo is None:
        raise ValueError('--worktree requires --repo')
    if not (inbox is not None or selected_worktrees or artifacts):
        raise ValueError('select results, worktrees or artifacts explicitly; use check for closeout')

    report = {
        'task': task_dir.name, 'mode': 'current', 'outcome': 'checked', 'issues': [],
        'checked': {'card': str(task_dir / 'task.md'), 'inbox': None,
                    'worktrees': [], 'artifacts': []},
        'not_checked': [
            'Other inboxes and unselected result artifacts, including historical results.',
            'Terminal, observer and process reconciliation; required closeout debts.',
            'Other worktrees and files not explicitly selected for hash verification.',
            'Checkout HEAD against a candidate pin; reported HEAD/dirty state is not candidate validation.',
            'Product acceptance, evidence applicability and permission to proceed.',
        ],
    }

    def issue(area, identity, detail):
        report['issues'].append({'area': area, 'identity': identity, 'detail': detail})

    try:
        card = card_of((task_dir / 'task.md').read_text())
        report['card'] = None if card is None else {
            'status': field(card, 'Status'), 'updated': field(card, 'Updated'),
            'expecting': field(card, 'Expecting'), 'next': field(card, 'Next')}
        if card is None or field(card, 'Status') not in STATUSES:
            issue('card', str(task_dir / 'task.md'), 'missing card or invalid task status')
    except (OSError, ValueError) as error:
        report['card'] = None
        issue('card', str(task_dir / 'task.md'), str(error))

    if inbox is not None:
        selected = {'path': str(inbox), 'selection': 'pending' if pending_results else 'exact_ids',
                    'results': {}, 'unselected_result_count': None}
        report['checked']['inbox'] = selected
        try:
            if not (inbox / 'lock').is_file():
                raise ValueError('selected inbox has no registration lock file')
            state = json.loads((inbox / 'state.json').read_text())
            entries = state['results']
            if not isinstance(entries, dict):
                raise ValueError('inbox results must be an object')
            selected['task'] = state['task']
            selected['mode'] = state['mode']
            if not isinstance(state['task'], str) or not state['task']:
                raise ValueError('inbox task must be a nonempty string')
            if state['mode'] not in ('active', 'waiting', 'paused', 'closed'):
                raise ValueError('unknown inbox mode')
            if pending_results:
                if any(not isinstance(entry, dict) for entry in entries.values()):
                    raise ValueError('cannot select pending results from malformed entries')
                identities = [identity for identity, entry in entries.items() if 'disposition' not in entry]
            else:
                identities = list(dict.fromkeys(result_ids))
            selected['unselected_result_count'] = len(set(entries) - set(identities))
            for identity in identities:
                try:
                    entry = entries[identity]
                    payload = entry['payload']
                    path = Path(payload['artifact'])
                    if not path.is_absolute():
                        raise ValueError('result artifact path must be absolute')
                    if payload.get('delivery_id', identity) != identity:
                        raise ValueError('result delivery ID differs from its inbox key')
                    if payload.get('task', state['task']) != state['task']:
                        raise ValueError('result task differs from its inbox registration')
                    record = current_artifact(path, payload['artifact_sha256'])
                    record['pending'] = 'disposition' not in entry
                    record['invalidated'] = 'invalidation' in entry
                    selected['results'][identity] = record
                    if record['status'] != 'matched':
                        issue('result', identity, record.get('error', 'artifact hash changed'))
                    if record['invalidated']:
                        issue('result', identity, 'result is invalidated; a matching hash does not reinstate it')
                except (KeyError, TypeError, ValueError) as error:
                    selected['results'][identity] = {'status': 'unknown', 'error': str(error)}
                    issue('result', identity, f'cannot inspect selected result: {error}')
        except (OSError, ValueError, KeyError, TypeError) as error:
            issue('inbox', str(inbox), f'cannot read selected inbox: {error}')

    for path in dict.fromkeys(selected_worktrees):
        record = current_worktree(path, repo)
        report['checked']['worktrees'].append(record)
        if record['status'] == 'unknown':
            issue('worktree', str(path), record['error'])

    for path, digest in artifacts:
        record = current_artifact(path, digest)
        report['checked']['artifacts'].append(record)
        if record['status'] != 'matched':
            issue('artifact', str(path), record.get('error', 'artifact hash changed'))
    if report['issues']:
        report['outcome'] = 'attention'
    return report


def main():
    """Expose explicit card operations so the current state is replaced rather than appended."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    put = sub.add_parser('set', help='Replace the card with the given text (file or - for stdin)')
    put.add_argument('--task-dir', required=True)
    put.add_argument('--card', required=True)
    show = sub.add_parser('show')
    show.add_argument('--task-dir', required=True)
    listing = sub.add_parser('list', help='Cards that are not closed, newest first')
    listing.add_argument('--runs', required=True)
    audit = sub.add_parser('check', help='Read-only closeout audit: card, inboxes, linked worktrees')
    audit.add_argument('--task-dir', required=True)
    audit.add_argument('--repo', required=True, help='Project repository to inspect; independent of the skill location')
    current = sub.add_parser('check-current', help='Read-only explicit scope check; does not replace closeout check')
    current.add_argument('--task-dir', required=True)
    current.add_argument('--inbox', help='One registered inbox; do not search task history')
    selection = current.add_mutually_exclusive_group()
    selection.add_argument('--pending-results', action='store_true', help='Hash only pending result artifacts in --inbox')
    selection.add_argument('--result-id', action='append', default=[], help='Exact result ID to verify in --inbox; repeatable')
    current.add_argument('--repo', help='Repository whose selected worktrees are inspected')
    current.add_argument('--worktree', action='append', default=[], help='Candidate/owner checkout root to inspect; repeatable')
    current.add_argument('--artifact', nargs=2, action='append', default=[], metavar=('PATH', 'SHA256'),
                         help='Explicit candidate/evidence file and expected hash; repeatable')
    args = parser.parse_args()
    try:
        if args.action == 'set':
            text = sys.stdin.read() if args.card == '-' else Path(args.card).read_text()
            print(write(Path(args.task_dir) / 'task.md', text))
        elif args.action == 'show':
            card = card_of((Path(args.task_dir) / 'task.md').read_text())
            if card is None:
                print('no task card', file=sys.stderr)
                return 1
            print(card)
        elif args.action == 'list':
            rows = []
            for task_md in Path(args.runs).glob('*/task.md'):
                card = card_of(task_md.read_text())
                if card is not None and field(card, 'Status') != 'closed':
                    rows.append((field(card, 'Updated') or '', task_md.parent.name, field(card, 'Status'),
                                 field(card, 'Next') or ''))
            for updated, name, status, upcoming in sorted(rows, reverse=True):
                print(f'{name}\t{status}\t{updated}\tNext: {upcoming}')
        elif args.action == 'check-current':
            report = check_current(
                Path(args.task_dir).resolve(), inbox=None if args.inbox is None else Path(args.inbox).resolve(),
                pending_results=args.pending_results, result_ids=args.result_id,
                repo=None if args.repo is None else Path(args.repo).resolve(),
                selected_worktrees=[Path(path).resolve() for path in args.worktree],
                artifacts=[(Path(path).resolve(), digest) for path, digest in args.artifact])
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1 if report['issues'] else 0
        else:
            print(json.dumps(check(Path(args.task_dir).resolve(), Path(args.repo)), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
