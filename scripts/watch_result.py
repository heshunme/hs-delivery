#!/usr/bin/env python3
"""Wake the coordinator when an expected result has not arrived by its deadline or its worker stopped without it."""

import argparse
import json
import math
import re
import subprocess
import sys
import time

from observer import bind, check_inbox_target, finish, is_stopped, stop_event
from queue_result import now, save_json

# Paseo agent statuses are initializing, idle, running, error and closed. A turn can no longer publish
# after `error` or `closed`; `idle` counts only once the worker was seen running and stays idle.
ENDED = {'closed', 'error'}
IDLE_READS = 2


def recorded(mailbox, delivery_id):
    """Read the inbox without changing its mode or wakeup."""
    from task_inbox import operate
    return delivery_id in operate(mailbox, 'status')['results']


def agent_status(agent, home=None):
    """Read one Paseo agent's status; a CLI failure is an observation error, not a dead worker."""
    command = ['paseo', 'inspect', agent, '--json']
    if home:
        command.extend(['--home', home])
    result = subprocess.run(command, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f'paseo inspect exited {result.returncode}: {result.stderr[-2000:]}')
    status = json.loads(result.stdout).get('Status')
    if not isinstance(status, str):
        raise ValueError('paseo inspect returned no status')
    return status.lower()


def observe(args, state, stopped):
    """Poll outside the model; publish only when the expected result is overdue or can no longer come."""
    deadline = time.monotonic() + args.max_wait
    seen_busy = False
    idle_reads = 0
    failures = 0
    status = None
    ready = False
    while True:
        if is_stopped(state, stopped):
            return {'outcome': 'stopped', 'agent_status': status}
        try:
            if recorded(args.mailbox, args.expect):
                return {'outcome': 'arrived', 'agent_status': status}
            if args.agent:
                status = agent_status(args.agent, args.paseo_home)
                seen_busy = seen_busy or status == 'running'
                # a queued round can start after a short idle gap, so one idle read is not an ended turn
                idle_reads = idle_reads + 1 if status == 'idle' and seen_busy else 0
                if status in ENDED or idle_reads >= IDLE_READS:
                    # the worker publishes before its turn ends, so one more inbox read settles the race
                    if recorded(args.mailbox, args.expect):
                        return {'outcome': 'arrived', 'agent_status': status}
                    return {'outcome': 'missing', 'agent_status': status,
                            'detail': 'worker turn ended without the expected result'}
            failures = 0
        except (OSError, ValueError, RuntimeError, KeyError, subprocess.TimeoutExpired) as failure:
            failures += 1
            save_json(state / 'status.json', {'observed_at': now(), 'phase': 'watching',
                                            'consecutive_errors': failures, 'error': str(failure)})
            if failures >= 3:
                return {'outcome': 'monitor_error', 'agent_status': status, 'detail': str(failure)}
        else:
            if not ready:
                save_json(state / 'ready.json', {'observed_at': now(), 'agent_status': status})
                print('READY ' + str(state / 'ready.json'), flush=True)
                ready = True
            save_json(state / 'status.json', {'observed_at': now(), 'phase': 'watching',
                                            'agent_status': status, 'seen_busy': seen_busy})
        if time.monotonic() >= deadline:
            return {'outcome': 'overdue', 'agent_status': status, 'detail': 'expected result not recorded by deadline'}
        stopped.wait(min(args.interval, max(0, deadline - time.monotonic())))


def main():
    """Bind one expected delivery ID to a registered inbox; a state directory is single-use."""
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ['task', 'expect', 'version', 'mailbox', 'state-dir']:
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--agent', help='Paseo agent ID of the worker; omit to watch the deadline only')
    parser.add_argument('--paseo-home')
    parser.add_argument('--thread', help='Registered coordinator Codex thread; omit for a harness inbox')
    parser.add_argument('--interval', type=float, default=120)
    parser.add_argument('--max-wait', type=float, required=True,
                        help='Seconds after which a still-missing result is reported as overdue')
    parser.add_argument('--remote')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}', args.expect):
        parser.error('expect must be the exact delivery ID assigned to the worker')
    if (not all(math.isfinite(value) for value in [args.interval, args.max_wait])
            or min(args.interval, args.max_wait) <= 0):
        parser.error('timing values must be positive')
    check_inbox_target(parser, args)
    state, binding = bind(vars(args), args.state_dir)
    if state is None:
        return 2
    stopped = stop_event()
    try:
        observation = observe(args, state, stopped)
    except Exception as error:
        observation = {'outcome': 'monitor_error', 'detail': f'{type(error).__name__}: {error}'}
    return finish(
        args, state, binding, stopped, observation,
        delivery_id=f'expect-{binding["observer_id"]}', version=args.version, sender='result observer',
        summary=f'{args.expect}: {observation["outcome"]}; reconcile the worker before reassigning',
        publish=observation['outcome'] != 'arrived',
    )


if __name__ == '__main__':
    sys.exit(main())
