#!/usr/bin/env python3
"""Observe one GitHub Actions run, then publish its durable task result."""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time

from observer import bind, check_inbox_target, finish, is_stopped, stop_event
from queue_result import now, save_json


def read_run(repo, run_id):
    """Read GitHub's authoritative attempt and SHA; a CLI error is not a CI failure."""
    result = subprocess.run(
        ['gh', 'api', f'repos/{repo}/actions/runs/{run_id}'],
        text=True, capture_output=True, timeout=30,
    )
    if result.returncode:
        raise RuntimeError(f'gh api exited {result.returncode}: {result.stderr[-2000:]}')
    raw = json.loads(result.stdout)
    keys = ['id', 'run_attempt', 'head_sha', 'status', 'conclusion', 'html_url', 'name', 'updated_at']
    record = {key: raw.get(key) for key in keys}
    if record['id'] != run_id or not isinstance(record['run_attempt'], int):
        raise ValueError('GitHub response has an invalid run identity')
    if not isinstance(record['head_sha'], str) or not isinstance(record['status'], str):
        raise ValueError('GitHub response is missing version/status')
    if record['status'] == 'completed' and not record['conclusion']:
        raise ValueError('completed run has no conclusion')
    return record


def observe(args, state, stopped):
    """Poll outside the model and stop at completion, replacement, error budget or deadline."""
    deadline = time.monotonic() + args.max_wait
    failures = 0
    last = None
    error = None
    ready = False
    while True:
        if is_stopped(state, stopped):
            return {'outcome': 'stopped', 'last_run': last, 'detail': 'monitoring explicitly stopped'}
        if time.monotonic() >= deadline:
            return {'outcome': 'deadline', 'last_run': last, 'detail': 'monitoring budget elapsed'}
        try:
            last = read_run(args.repo, args.run_id)
            failures = 0
            error = None
            save_json(state / 'latest.json', {'observed_at': now(), 'run': last})
            if last['head_sha'] != args.sha or last['run_attempt'] != args.attempt:
                return {'outcome': 'superseded', 'last_run': last, 'detail': 'SHA or attempt differs from binding'}
            if not ready:
                save_json(state / 'ready.json', {'observed_at': now(), 'pid': os.getpid(), 'run': last})
                print('READY ' + str(state / 'ready.json'), flush=True)
                ready = True
            if last['status'] == 'completed':
                return {'outcome': 'completed', 'last_run': last}
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as failure:
            failures += 1
            error = str(failure)
        save_json(state / 'status.json', {
            'observed_at': now(), 'phase': 'watching', 'consecutive_errors': failures, 'error': error,
        })
        if failures >= 3:
            return {'outcome': 'monitor_error', 'last_run': last, 'detail': error}
        # An Event permits immediate SIGTERM cancellation without running a model loop.
        stopped.wait(min(args.interval, max(0, deadline - time.monotonic())))


def main():
    """Bind a finite observer to explicit task coordinates; a state directory is single-use."""
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ['task', 'repo', 'sha', 'state-dir']:
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--thread', help='Registered coordinator Codex thread; omit for a harness inbox')
    parser.add_argument('--run-id', required=True, type=int)
    parser.add_argument('--attempt', required=True, type=int)
    parser.add_argument('--interval', type=float, default=60)
    parser.add_argument('--max-wait', type=float, default=7200)
    parser.add_argument('--remote')
    parser.add_argument('--mailbox', help='Registered coordinator inbox; required for new workflow tasks')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', args.repo):
        parser.error('repo must be OWNER/REPOSITORY')
    if not re.fullmatch(r'[0-9a-f]{40}', args.sha):
        parser.error('sha must be a full lowercase Git commit SHA')
    if (not all(math.isfinite(value) for value in [args.interval, args.max_wait])
            or min(args.run_id, args.attempt, args.interval, args.max_wait) <= 0):
        parser.error('run ID, attempt and timing values must be positive')
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
        delivery_id=f'ci-{args.run_id}-attempt-{args.attempt}-{binding["observer_id"]}',
        version=args.sha, sender='CI watcher',
        summary=f'{args.repo} run {args.run_id}: {observation["outcome"]}; reconcile result before closeout',
    )


if __name__ == '__main__':
    sys.exit(main())
