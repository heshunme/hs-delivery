"""Inspect or remove one recorded task wakeup without loading its Codex thread."""

import asyncio
import json
from pathlib import Path
import subprocess
import sys


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

    def __init__(self, remote, *, timeout=15):
        remote = local_remote(remote)
        if sys.version_info < (3, 11):
            raise RuntimeError('Queue transport requires Python 3.11+; core helpers support Python 3.9+')
        # Standard-library-only inbox operations must not require the optional transport.
        try:
            from websockets.asyncio.client import unix_connect
            from websockets.exceptions import WebSocketException
        except ImportError as error:
            requirements = Path(__file__).resolve().parents[1] / 'requirements-queue.txt'
            raise RuntimeError(
                f'Queue transport requires Python 3.11+ and websockets; '
                f'install {requirements} into the interpreter running these helpers'
            ) from error
        self.timeout = timeout
        self._websocket_errors = WebSocketException
        self.runner = asyncio.Runner()
        self.connection = None
        self.sequence = 0

        async def open_connection():
            return await unix_connect(
                remote[7:], open_timeout=10, close_timeout=3, proxy=None,
                compression=None, ping_interval=None, max_size=100 * 1024 * 1024,
            )

        try:
            self.connection = self._run(open_connection())
            self.call('initialize', {'clientInfo': {'name': 'hs-delivery-inbox', 'version': '1'},
                                     'capabilities': {'experimentalApi': True}})
            self.send({'method': 'initialized', 'params': {}})
        except BaseException:
            self.close()
            raise

    def close(self):
        """Close this client only; preserve the server and thread owner."""
        if self.runner is None:
            return
        try:
            if self.connection is not None:
                self._run(self.connection.close())
        finally:
            self.runner.close()
            self.runner = None

    def _run(self, operation):
        """Keep the synchronous interface while bounding each complete network operation."""
        async def bounded():
            return await asyncio.wait_for(operation, timeout=self.timeout)

        try:
            return self.runner.run(bounded())
        except TimeoutError as error:
            raise TimeoutError('Codex queue control timed out') from error
        except self._websocket_errors as error:
            raise RuntimeError(f'Codex queue control connection failed: {error}') from error

    def send(self, value):
        """Serialize one native protocol message."""
        self._run(self.connection.send(json.dumps(value)))

    def call(self, method, params):
        """Wait for a matching response, with a finite I/O budget."""
        self.sequence += 1
        return self._run(self._request(self.sequence, method, params))

    async def _request(self, identity, method, params):
        """Ignore unrelated notifications without extending the request deadline."""
        await self.connection.send(json.dumps({'id': identity, 'method': method, 'params': params}))
        while True:
            value = json.loads(await self.connection.recv())
            if not isinstance(value, dict):
                raise ValueError('Codex queue control received a non-object message')
            if value.get('id') == identity and 'method' not in value:
                if 'error' in value:
                    raise RuntimeError(json.dumps(value['error']))
                return value['result']

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
