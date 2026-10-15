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
    entries = []
    # the first entry is the main checkout itself
    for chunk in result.stdout.strip().split('\n\n')[1:]:
        info = dict(line.split(' ', 1) for line in chunk.splitlines() if ' ' in line)
        path = info.get('worktree', '')
        if not path:
            continue
        status = subprocess.run(['git', '-C', path, 'status', '--porcelain'],
                                text=True, capture_output=True, timeout=30)
        entries.append({'path': path, 'branch': info.get('branch'), 'dirty': bool(status.stdout.strip()),
                        'prunable': any(line.startswith('prunable') for line in chunk.splitlines())})
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
        else:
            print(json.dumps(check(Path(args.task_dir).resolve(), Path(args.repo)), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
