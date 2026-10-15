#!/usr/bin/env python3
"""Publish an artifact result to a registered inbox, or submit it to a Codex thread once."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid


def now():
    """Return a timestamp suitable for cross-session evidence."""
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    """Replace a complete JSON record without exposing partially written content."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.{os.getpid()}.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def submit(*, thread, message, remote=None, cancelled=None):
    """Submit one input with a bounded CLI wait; callers persist intent first."""
    command = ['codex', 'queue', '--thread', thread, '--message', message]
    if remote:
        command.extend(['--remote', remote])
    try:
        if cancelled is not None and cancelled():
            raise RuntimeError('notification cancelled before CLI launch')
        process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 45
        while True:
            try:
                stdout, stderr = process.communicate(timeout=0.2)
                break
            except subprocess.TimeoutExpired:
                if (cancelled is not None and cancelled()) or time.monotonic() >= deadline:
                    process.kill()
                    process.communicate()
                    raise RuntimeError('queue wait cancelled or expired; acceptance may already have occurred')
        receipt = {
            'observed_at': now(), 'status': 'accepted' if process.returncode == 0 else 'uncertain',
            'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr,
        }
    except (OSError, RuntimeError) as error:
        receipt = {'observed_at': now(), 'status': 'uncertain', 'error': str(error)}
    return receipt


def deliver(*, task, delivery_id, sender, artifact, version, summary, outbox, thread=None, remote=None, cancelled=None, mailbox=None):
    """Publish to a registered inbox, or enqueue once; an uncertain intent requires reconciliation."""
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}', delivery_id):
        raise ValueError('delivery ID must be a short filename-safe identifier')
    if thread is None and mailbox is None:
        raise ValueError('direct queue delivery needs the recipient thread')
    if thread is not None:
        thread = str(uuid.UUID(thread))
    artifact = Path(artifact).resolve(strict=True)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    payload = {
        'task': task, 'delivery_id': delivery_id, 'sender': sender,
        'thread': thread, 'remote': remote, 'artifact': str(artifact),
        'artifact_sha256': digest, 'version': version, 'summary': summary,
    }
    if mailbox is not None:
        from task_inbox import publish
        return publish(mailbox, payload, outbox=outbox, cancelled=cancelled)
    message = (
        'Agent handoff within the existing authorized task; not a new maintainer instruction.\n'
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + '\nRead the artifact, verify its version/hash and current task membership, and '
        'continue the assigned task. If this delivery ID was already handled, do not repeat '
        'its effects or send an acknowledgment loop. A watcher observation is not delivery approval.'
    )
    outbox = Path(outbox).resolve()
    outbox.mkdir(parents=True, exist_ok=True)
    intent_path = outbox / f'{delivery_id}.intent.json'
    receipt_path = outbox / f'{delivery_id}.receipt.json'
    try:
        stream = intent_path.open('x')
    except FileExistsError:
        intent = json.loads(intent_path.read_text())
        if intent['payload'] != payload:
            raise RuntimeError('delivery ID already binds different content; inspect the existing intent')
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt.get('status') == 'accepted':
                return receipt
        raise RuntimeError('delivery outcome uncertain; reconcile transcript/queue before any resend')
    with stream:
        json.dump({'created_at': now(), 'payload': payload, 'message': message}, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    receipt = submit(thread=thread, message=message, remote=remote, cancelled=cancelled)
    save_json(receipt_path, receipt)
    if receipt['status'] != 'accepted':
        raise RuntimeError(f'queue outcome uncertain; inspect {receipt_path}; no automatic retry')
    return receipt


def main():
    """Read explicit recipient and artifact coordinates, never infer task membership."""
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ['task', 'delivery-id', 'sender', 'artifact', 'version', 'summary', 'outbox']:
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--thread', help='Registered coordinator Codex thread; omit for a harness inbox')
    parser.add_argument('--remote')
    parser.add_argument('--mailbox', help='Registered coordinator inbox for result publication')
    args = vars(parser.parse_args())
    try:
        print(json.dumps(deliver(**args), ensure_ascii=False))
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
