#!/usr/bin/env python3
"""Collect task results, arm one idle wakeup when the host needs one, and reconcile owned terminals."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import uuid

from queue_control import local_remote, retire
from queue_result import now, save_json, submit


@contextmanager
def locked(mailbox):
    """Serialize publishers and the coordinator across local processes."""
    if not mailbox:
        # Path('') would silently resolve to the caller's working directory
        raise ValueError('inbox path is empty')
    root = Path(mailbox).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'lock').open('a') as handle:
        deadline = time.monotonic() + 60
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError('inbox lock timed out; inspect its current writer')
                time.sleep(0.05)
        try:
            yield root
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def load(root):
    """Require explicit registration rather than deriving recipient membership."""
    return json.loads((root / 'state.json').read_text())


def pending(state):
    """Expose only results that have not received an explicit disposition."""
    return [x for x in state['results'].values() if 'disposition' not in x]


def validate_publisher(mailbox, task, thread, remote=None):
    """Reject an unregistered or mismatched observer before it advertises readiness."""
    with locked(mailbox) as root:
        state = load(root)
        if (task, thread) != (state['task'], state['thread']):
            raise ValueError('observer task/thread differs from the registered inbox')
        if remote not in (None, state['remote']):
            raise ValueError('observer endpoint differs from the registered inbox')
        if state['mode'] in ('paused', 'closed'):
            raise RuntimeError('cannot start an observer for a paused/closed inbox')
        return state['remote']


def wake_transport(state):
    """An inbox without a recorded transport wakes a Codex thread."""
    return state.get('transport', 'codex-queue')


def initialize(mailbox, task, thread=None, remote=None, transport='harness'):
    """Bind a fresh mailbox permanently to one task and coordinator."""
    if transport == 'harness':
        # the host's own completion notices wake the coordinator; nothing here can address it
        if thread is not None or remote is not None:
            raise ValueError('a harness inbox has no Codex thread or endpoint')
    else:
        if thread is None:
            raise ValueError('a codex-queue inbox needs the coordinator thread')
        thread = str(uuid.UUID(thread))
        remote = local_remote(remote)
    with locked(mailbox) as root:
        if (root / 'state.json').exists():
            raise RuntimeError('mailbox exists; inspect it rather than reinitialize')
        state = {'task': task, 'transport': transport, 'thread': thread, 'remote': remote, 'created_at': now(),
                 'mode': 'active', 'results': {}, 'wake': None, 'wake_history': [], 'terminals': {}}
        save_json(root / 'state.json', state)
        return state


def notify(root, state, cancelled):
    """Publish a single inbox pointer; retain uncertain sends without retrying."""
    identity = uuid.uuid4().hex
    message = (f'Agent result notification for existing task {state["task"]}; not a new maintainer instruction.\n'
               f'Inbox: {root}\nWake ID: {identity}\n'
               'Use task_inbox.py take, reconcile all unprocessed results and acknowledge only '
               'their exact IDs/hashes. This wakeup carries no individual result or delivery approval. '
               'An empty batch needs no user-facing acknowledgment. Respect the current task scope and stop state.')
    wake = {'id': identity, 'message': message, 'status': 'intent', 'created_at': now()}
    state['wake'] = wake
    save_json(root / 'state.json', state)
    receipt = submit(thread=state['thread'], message=message, remote=state['remote'], cancelled=cancelled)
    match = re.search(r'Queued message ([0-9a-f-]{36}) for thread ([0-9a-f-]{36})', receipt.get('stdout', ''))
    wake['receipt'] = receipt
    if receipt['status'] == 'accepted' and match and match[2] == state['thread']:
        wake.update(status='accepted', queue_id=str(uuid.UUID(match[1])))
    else:
        wake['status'] = 'uncertain'
    save_json(root / 'state.json', state)


def publish(mailbox, payload, *, outbox, cancelled=None):
    """Retain every result; active/paused coordinators get no queued wakeup."""
    with locked(mailbox) as root:
        state = load(root)
        if payload['task'] != state['task'] or payload['thread'] != state['thread']:
            raise ValueError('result does not belong to the registered task/coordinator')
        if payload['remote'] not in (None, state['remote']):
            raise ValueError('result endpoint differs from the registered inbox')
        if state['mode'] == 'closed':
            raise RuntimeError('task inbox is closed; do not wake or reopen it')
        if cancelled is not None and cancelled():
            raise RuntimeError('result publication cancelled')
        identity = payload['delivery_id']
        existing = state['results'].get(identity)
        if existing is not None and existing['payload'] != payload:
            raise RuntimeError('delivery ID already binds a different result')
        if existing is None:
            state['results'][identity] = {'payload': payload, 'recorded_at': now()}
            save_json(root / 'state.json', state)
        if (wake_transport(state) == 'codex-queue' and state['mode'] == 'waiting'
                and state['wake'] is None and pending(state)):
            notify(root, state, cancelled)
        receipt = {'status': 'recorded', 'mailbox': str(root), 'delivery_id': identity,
                   'observed_at': now(), 'wake_status': (state['wake'] or {}).get('status')}
        # This receipt proves result persistence, not that any model has consumed it.
        save_json(Path(outbox) / f'{identity}.receipt.json', receipt)
        if state['wake'] is not None and state['wake']['status'] in ('intent', 'uncertain'):
            raise RuntimeError('result retained but wake outcome uncertain; reconcile, never resend blindly')
        return receipt


def activate(root, state):
    """Withdraw this task's pending wakeup before processing its durable results."""
    if state['mode'] in ('paused', 'closed'):
        raise RuntimeError('inbox is paused/closed; explicit authorized resume is required')
    state['mode'] = 'active'
    save_json(root / 'state.json', state)
    wake = state['wake']
    if wake is None:
        return
    if wake['status'] != 'accepted':
        raise RuntimeError('wake outcome uncertain; inspect queue/transcript before resolving it')
    disposition = retire(state['remote'], state['thread'], wake)
    state['wake_history'].append({**wake, 'retired_at': now(), 'disposition': disposition})
    state['wake'] = None
    save_json(root / 'state.json', state)


def operate(mailbox, action, **args):
    """Apply coordinator transitions under the same lock as result publication."""
    with locked(mailbox) as root:
        state = load(root)
        if action == 'status':
            return state
        if action == 'take':
            activate(root, state)
            return {'mode': state['mode'], 'results': pending(state)}
        if action == 'ack':
            activate(root, state)
            entry = state['results'][args['delivery_id']]
            if 'invalidation' in entry:
                raise ValueError('invalidated evidence cannot be acknowledged; publish a correction')
            payload = entry['payload']
            digest = hashlib.sha256(Path(payload['artifact']).read_bytes()).hexdigest()
            if digest != args['sha256'] or digest != payload['artifact_sha256']:
                raise ValueError('artifact digest changed or does not match the reviewed result')
            if 'disposition' in entry and entry['disposition'] != args['disposition']:
                raise ValueError('result already has a different disposition')
            entry.update(disposition=args['disposition'], processed_at=entry.get('processed_at', now()))
        elif action == 'invalidate':
            identity = args['delivery_id']
            entry = state['results'][identity]
            if args['sha256'] != entry['payload']['artifact_sha256']:
                raise ValueError('invalidation must identify the original recorded artifact digest')
            reason = args['reason'].strip()
            if not reason:
                raise ValueError('invalidation needs a reason')
            replacement = args.get('superseded_by')
            invalidation = {'reason': reason, 'superseded_by': replacement}
            if 'disposition' in entry:
                if entry.get('invalidation') != invalidation:
                    raise ValueError('result already has a different disposition')
            elif replacement is not None:
                if replacement == identity or replacement not in state['results']:
                    raise ValueError('replacement must be another result in this inbox')
                if 'invalidation' in state['results'][replacement]:
                    raise ValueError('replacement is itself invalidated')
            activate(root, state)
            # Missing or overwritten bytes may be discarded, never treated as reviewed evidence.
            entry.update(invalidation=invalidation, disposition=f'invalidated: {reason}',
                         processed_at=entry.get('processed_at', now()))
        elif action == 'wait':
            activate(root, state)
            if pending(state):
                return {'mode': 'active', 'ready': True, 'results': pending(state)}
            state['mode'] = 'waiting'
        elif action == 'pause':
            if state['mode'] == 'closed':
                raise RuntimeError('closed inbox cannot be paused or reopened')
            # Persist pause first even if retiring a queued wakeup fails.
            state['mode'] = 'paused'
            save_json(root / 'state.json', state)
            if state['wake']:
                wake = state['wake']
                if wake['status'] != 'accepted':
                    raise RuntimeError('paused with uncertain wake; inspect rather than retry')
                outcome = retire(state['remote'], state['thread'], wake)
                state['wake_history'].append({**wake, 'retired_at': now(), 'disposition': outcome})
                state['wake'] = None
        elif action == 'resume':
            if state['mode'] != 'paused':
                raise RuntimeError('only an explicitly paused inbox can resume')
            state['mode'] = 'active'
        elif action == 'terminal-add':
            if state['mode'] != 'active':
                raise RuntimeError('register resources only during active authorized work')
            identity = str(uuid.UUID(args['terminal_id']))
            if identity in state['terminals']:
                raise RuntimeError('terminal already registered')
            state['terminals'][identity] = {'state_dir': str(Path(args['state_dir']).resolve()),
                                            'registered_at': now(), 'status': 'owned'}
        elif action == 'terminals-reconcile':
            snapshot = Path(args['snapshot'])
            raw = json.loads(snapshot.read_text())
            captured = datetime.fromisoformat(raw['captured_at'])
            age = (datetime.now(timezone.utc) - captured).total_seconds()
            if raw.get('scope') != 'all' or not 0 <= age <= 60:
                raise ValueError('use a fresh all-terminals host snapshot (within 60 seconds)')
            if any(captured < datetime.fromisoformat(x['registered_at']) for x in state['terminals'].values()):
                raise ValueError('terminal snapshot predates resource registration')
            terminals = raw['terminals']
            present = {x['id'] for x in terminals}
            for identity, entry in state['terminals'].items():
                entry.update(status='present' if identity in present else 'removed', checked_at=now(),
                             snapshot=str(snapshot.resolve()),
                             snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
        elif action == 'close':
            activate(root, state)
            if pending(state) or any(x['status'] != 'removed' for x in state['terminals'].values()):
                raise RuntimeError('unprocessed results or unreconciled owned terminals remain')
            state['mode'] = 'closed'
            state['closed_at'] = now()
        else:
            raise ValueError('unknown inbox operation')
        save_json(root / 'state.json', state)
        return {'mode': state['mode'], 'pending': len(pending(state)), 'terminals': state['terminals']}


def main():
    """Expose explicit actions so ending a turn cannot silently mark results handled."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mailbox', required=True)
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init')
    init.add_argument('--task', required=True)
    init.add_argument('--transport', choices=['codex-queue', 'harness'], default='harness',
                      help='How a waiting coordinator is woken: a queued Codex input, or its own host')
    init.add_argument('--thread', help='Coordinator Codex thread UUID; codex-queue only')
    init.add_argument('--remote')
    for action in ['status', 'take', 'wait', 'pause', 'resume', 'close']:
        sub.add_parser(action)
    ack = sub.add_parser('ack')
    for field in ['delivery-id', 'sha256', 'disposition']:
        ack.add_argument('--' + field, required=True)
    invalidate = sub.add_parser('invalidate', help='Discard unusable evidence without approving its replacement')
    for field in ['delivery-id', 'sha256', 'reason']:
        invalidate.add_argument('--' + field, required=True)
    invalidate.add_argument('--superseded-by', help='Existing correction delivery ID in the same inbox')
    terminal = sub.add_parser('terminal-add')
    terminal.add_argument('--terminal-id', required=True)
    terminal.add_argument('--state-dir', required=True)
    reconcile = sub.add_parser('terminals-reconcile')
    reconcile.add_argument('--snapshot', required=True)
    args = vars(parser.parse_args())
    action = args.pop('action')
    mailbox = args.pop('mailbox')
    try:
        result = initialize(mailbox, **args) if action == 'init' else operate(mailbox, action, **args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
