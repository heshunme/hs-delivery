"""Inspect or remove one recorded task wakeup without loading its Codex thread."""

import json
import os
from pathlib import Path
import select
import subprocess
import time


def local_remote(remote=None):
    """Pin queue submission and cleanup to the same existing local endpoint."""
    if remote is None:
        result = subprocess.run(['codex', 'app-server', 'daemon', 'version'],
                                capture_output=True, text=True, timeout=15, check=True)
        daemon = json.loads(result.stdout)
        if daemon.get('status') != 'running':
            raise RuntimeError('start the local Codex daemon before registering an inbox')
        remote = 'unix://' + daemon['socketPath']
    if not remote.startswith('unix:///'):
        raise ValueError('inbox cleanup supports an explicit local Unix endpoint only')
    return remote


class QueueControl:
    """Bounded local JSON-RPC connection; never resume, start or interrupt a thread."""

    def __init__(self, remote):
        # Keep the optional transport inside the skill, independent of the target checkout.
        bridge = Path(__file__).resolve().with_name('queue_bridge.cjs')
        if not bridge.is_file():
            raise FileNotFoundError(f'Queue bridge is missing: {bridge}')
        self.process = subprocess.Popen(
            ['node', str(bridge), remote[7:]],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        self.buffer = b''
        self.sequence = 0
        try:
            self.call('initialize', {'clientInfo': {'name': 'hs-delivery-inbox', 'version': '1'},
                                     'capabilities': {'experimentalApi': True}})
            self.send({'method': 'initialized', 'params': {}})
        except Exception:
            self.close()
            raise

    def close(self):
        """Close this client only; preserve the server and thread owner."""
        self.process.terminate()
        try:
            self.process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.communicate()

    def send(self, value):
        """Serialize one native protocol message."""
        self.process.stdin.write((json.dumps(value) + '\n').encode())
        self.process.stdin.flush()

    def call(self, method, params):
        """Wait for a matching response, with a finite I/O budget."""
        self.sequence += 1
        identity = self.sequence
        self.send({'id': identity, 'method': method, 'params': params})
        deadline = time.monotonic() + 15
        while True:
            while b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                value = json.loads(line)
                if value.get('id') == identity and 'method' not in value:
                    if 'error' in value:
                        raise RuntimeError(json.dumps(value['error']))
                    return value['result']
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.process.stdout], [], [], remaining)[0]:
                raise TimeoutError('Codex queue control timed out')
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError('Codex queue control disconnected')
            self.buffer += chunk

    def pending(self, thread):
        """Read queue pages without subscribing to or loading the recipient."""
        cursor = None
        for _ in range(100):
            params = {'threadId': thread, 'limit': 100}
            if cursor is not None:
                params['cursor'] = cursor
            page = self.call('thread/queue/list', params)
            yield from page['data']
            cursor = page.get('nextCursor')
            if cursor is None:
                return
        raise RuntimeError('queue too large to reconcile within the bounded scan')


def retire(remote, thread, wake):
    """Delete only the exact saved ID/text; already-started input cannot be recalled."""
    client = QueueControl(remote)
    try:
        item = next((x for x in client.pending(thread) if x['id'] == wake['queue_id']), None)
        if item is None:
            return 'absent_or_started'
        texts = [x.get('text') for x in item['input'] if x.get('type') == 'text']
        if texts != [wake['message']] or len(item['input']) != 1:
            raise RuntimeError('recorded queue ID has different content; refusing removal')
        result = client.call('thread/queue/delete', {
            'threadId': thread, 'queuedSubmissionId': wake['queue_id']})
        return 'deleted' if result['deleted'] else 'absent_or_started'
    finally:
        client.close()
