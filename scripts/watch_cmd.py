#!/usr/bin/env python3
"""Run one local command outside the model, then publish its exit to the task inbox."""

import argparse
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

from observer import bind, check_inbox_target, finish, is_stopped, stop_event
from queue_result import now, save_json


def source_identity(cwd):
    """Record what the command ran against: HEAD plus whether the tree had local changes."""
    def git(*command):
        result = subprocess.run(['git', '-C', str(cwd), *command], text=True, capture_output=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else None
    head = git('rev-parse', 'HEAD')
    if head is None:
        return {'head': None, 'dirty': None, 'version': 'not-a-git-checkout'}
    dirty = bool(git('status', '--porcelain', '--untracked-files=normal'))
    return {'head': head, 'dirty': dirty, 'version': head + ('+dirty' if dirty else '')}


def tail(path, lines=40):
    """Keep the end of the log in the result so the coordinator can triage without opening it."""
    try:
        with path.open('rb') as stream:
            stream.seek(0, os.SEEK_END)
            stream.seek(max(0, stream.tell() - 64 * 1024))
            text = stream.read().decode('utf-8', 'replace')
    except OSError:
        return []
    return text.splitlines()[-lines:]


def kill_group(child, signum):
    """Signal the child's process group; a group that already exited is not an error."""
    try:
        os.killpg(child.pid, signum)
    except ProcessLookupError:
        pass


def run(args, state, stopped, log):
    """Wait for the child without polling the model; a stop or deadline ends its whole process group."""
    if is_stopped(state, stopped):
        return {'outcome': 'stopped', 'exit_code': None, 'duration_s': 0,
                'log': str(log), 'log_tail': []}
    with log.open('ab') as output:
        child = subprocess.Popen(args.command, cwd=args.cwd, stdin=subprocess.DEVNULL, stdout=output,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    save_json(state / 'ready.json', {'observed_at': now(), 'pid': os.getpid(), 'child_pid': child.pid})
    save_json(state / 'status.json', {'observed_at': now(), 'phase': 'running', 'child_pid': child.pid})
    print('READY ' + str(state / 'ready.json'), flush=True)
    started = time.monotonic()
    deadline = started + args.max_wait
    outcome = None
    while child.poll() is None:
        if is_stopped(state, stopped):
            outcome = 'stopped'
        elif time.monotonic() >= deadline:
            outcome = 'deadline'
        if outcome:
            kill_group(child, signal.SIGTERM)
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                kill_group(child, signal.SIGKILL)
                child.wait()
            break
        stopped.wait(1)
    elapsed = round(time.monotonic() - started, 1)
    if outcome is None:
        outcome = 'succeeded' if child.returncode == 0 else 'failed'
    return {'outcome': outcome, 'exit_code': child.returncode, 'duration_s': elapsed,
            'log': str(log), 'log_tail': tail(log)}


def main():
    """Bind one command to explicit task coordinates; a state directory is single-use."""
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ['task', 'label', 'state-dir']:
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--cwd', default='.', help='Directory the command runs in; its Git state is recorded')
    parser.add_argument('--log', help='Combined stdout/stderr file, relative to --cwd; defaults to <state-dir>/command.log')
    parser.add_argument('--thread', help='Registered coordinator Codex thread; omit for a harness inbox')
    parser.add_argument('--max-wait', type=float, default=7200)
    parser.add_argument('--remote')
    parser.add_argument('--mailbox', help='Registered coordinator inbox')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='-- followed by the command and its arguments')
    args = parser.parse_args()
    if args.command[:1] == ['--']:
        args.command = args.command[1:]
    if not args.command:
        parser.error('pass the command after --')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,59}', args.label):
        parser.error('label must be a short filename-safe identifier')
    if not math.isfinite(args.max_wait) or args.max_wait <= 0:
        parser.error('max-wait must be positive')
    args.cwd = str(Path(args.cwd).resolve(strict=True))
    check_inbox_target(parser, args)
    identity = source_identity(args.cwd)
    state, binding = bind({**vars(args), 'source': identity}, args.state_dir)
    if state is None:
        return 2
    log = (Path(args.cwd) / args.log).resolve() if args.log else state / 'command.log'
    stopped = stop_event()
    try:
        observation = run(args, state, stopped, log)
    except Exception as error:
        observation = {'outcome': 'monitor_error', 'detail': f'{type(error).__name__}: {error}'}
    # a hook commit moves HEAD; the result must name the commit it made, not its parent
    try:
        after = source_identity(args.cwd)
    except (OSError, subprocess.TimeoutExpired) as error:
        after = {'head': identity['head'], 'dirty': None, 'version': identity['version'],
                 'error': f'{type(error).__name__}: {error}'}
    observation['after'] = after
    return finish(
        args, state, binding, stopped, observation,
        delivery_id=f'cmd-{args.label}-{binding["observer_id"]}',
        version=after['version'] if after['head'] != identity['head'] else identity['version'],
        sender='command observer',
        summary=f'{args.label}: {observation["outcome"]} (exit {observation.get("exit_code")}); read result before relying on it',
    )


if __name__ == '__main__':
    sys.exit(main())
