"""Shared lifecycle for finite observers: single-use binding, stop signals and one durable publication."""

import json
import os
from pathlib import Path
import signal
import sys
import threading
import uuid

from queue_result import deliver, now, save_json


def check_inbox_target(parser, args):
    """Normalize the coordinator address and reject an unregistered inbox before any work starts."""
    if args.thread is None and args.mailbox is None:
        parser.error('pass the registered --mailbox, or --thread for direct Codex delivery')
    if args.thread is not None:
        try:
            args.thread = str(uuid.UUID(args.thread))
        except ValueError:
            parser.error('thread must be the registered native Codex UUID')
    if args.mailbox is not None:
        from task_inbox import validate_publisher
        try:
            validate_publisher(args.mailbox, args.task, args.thread, args.remote)
        except (OSError, ValueError, RuntimeError, KeyError) as error:
            parser.error(str(error))


def bind(fields, state_dir):
    """Create the binding exclusively; return None when the state directory was already used."""
    state = Path(state_dir).resolve()
    state.mkdir(parents=True, exist_ok=True)
    binding = {**fields, 'state_dir': str(state), 'started_at': now(), 'pid': os.getpid(),
               'observer_id': uuid.uuid4().hex}
    try:
        stream = (state / 'binding.json').open('x')
    except FileExistsError:
        print('state already exists; inspect it rather than restart or resend blindly', file=sys.stderr)
        return None, None
    with stream:
        json.dump(binding, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return state, binding


def stop_event():
    """Turn SIGINT/SIGTERM/SIGHUP into an Event so waits end promptly without a model loop."""
    stopped = threading.Event()
    # a closed host terminal sends SIGHUP; dying on it would orphan whatever the observer runs
    for signum in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
        # a launcher that deliberately ignores hangups (nohup) keeps that choice
        if signum == signal.SIGHUP and signal.getsignal(signum) == signal.SIG_IGN:
            continue
        signal.signal(signum, lambda *_: stopped.set())
    return stopped


def is_stopped(state, stopped):
    """Report an explicit stop by signal or STOP file."""
    return stopped.is_set() or (state / 'STOP').exists()


def finish(args, state, binding, stopped, observation, *, delivery_id, version, summary, sender, publish=True):
    """Write the immutable result, then publish it once unless stopped; return the process exit code."""
    if is_stopped(state, stopped):
        observation['outcome'] = 'stopped'
    artifact = state / 'result.json'
    save_json(artifact, {**binding, 'finished_at': now(), **observation})
    if observation['outcome'] == 'stopped':
        save_json(state / 'status.json', {'phase': 'stopped', 'observed_at': now(), 'notification': 'suppressed'})
        return 0
    if not publish:
        # the observed result reached the inbox by itself; a second notice would only add noise
        save_json(state / 'status.json', {'phase': 'unpublished', 'observed_at': now(),
                                        'outcome': observation['outcome']})
        return 0
    try:
        receipt = deliver(
            task=args.task, delivery_id=delivery_id, sender=sender, thread=args.thread,
            artifact=artifact, version=version, summary=summary,
            outbox=state / 'outbox', remote=args.remote, mailbox=args.mailbox,
            cancelled=lambda: is_stopped(state, stopped),
        )
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        save_json(state / 'status.json', {'phase': 'notification_uncertain', 'observed_at': now(), 'error': str(error)})
        print(str(error), file=sys.stderr)
        return 2
    phase = 'recorded' if receipt['status'] == 'recorded' else 'notified'
    save_json(state / 'status.json', {'phase': phase, 'observed_at': now(), 'delivery_id': delivery_id,
                                    'mailbox': args.mailbox})
    print(phase.upper() + ' ' + str(artifact), flush=True)
    return 0


def inspect_state(state_dir):
    """Read observer evidence without repairing it or inferring process liveness."""
    root = Path(state_dir)
    report = {'state_dir': str(root), 'process_liveness': 'not_checked', 'errors': []}
    for name in ('binding', 'status', 'result'):
        try:
            value = json.loads((root / f'{name}.json').read_text())
            if not isinstance(value, dict):
                raise ValueError('expected a JSON object')
            # Bindings may contain command arguments; expose only lifecycle identifiers.
            fields = {'binding': ('observer_id', 'task', 'expect', 'pid', 'started_at'),
                      'status': ('phase', 'observed_at', 'outcome', 'notification', 'consecutive_errors', 'error'),
                      'result': ('outcome', 'finished_at', 'agent_status')}[name]
            report[name] = {key: value[key] for key in fields if key in value}
        except FileNotFoundError:
            report[name] = None
        except (OSError, ValueError) as error:
            report[name] = None
            report['errors'].append({'file': name + '.json', 'error': str(error)})
    return report
