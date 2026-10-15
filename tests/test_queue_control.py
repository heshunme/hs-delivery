"""Exercise direct Python queue connections against a disposable Unix WebSocket server."""

import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from queue_control import QueueControl, retire

try:
    from websockets.exceptions import ConnectionClosed
    from websockets.sync.server import unix_serve
except ModuleNotFoundError:
    unix_serve = None


class QueueServer:
    """Run a controllable local protocol peer with explicit shutdown."""

    def __init__(self, reply):
        self.directory = tempfile.TemporaryDirectory(prefix='hs-queue-')
        self.path = str(Path(self.directory.name) / 'queue.sock')
        self.remote = 'unix://' + self.path
        self.calls = []
        self.closed = threading.Event()
        self.initialization_error = None
        self.reply = reply
        self.server = unix_serve(self.handle, self.path, compression=None,
                                 ping_interval=None, close_timeout=1)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def handle(self, connection):
        try:
            for message in connection:
                request = json.loads(message)
                self.calls.append(request)
                if 'id' not in request:
                    continue
                if request['method'] == 'initialize':
                    response = ({'id': request['id'], 'error': self.initialization_error}
                                if self.initialization_error is not None
                                else {'id': request['id'], 'result': {}})
                else:
                    response = self.reply(connection, request)
                if response is not None:
                    connection.send(json.dumps(response))
        except ConnectionClosed:
            pass
        finally:
            self.closed.set()

    def close(self):
        self.server.shutdown()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise RuntimeError('fixture server did not stop')
        self.directory.cleanup()


@unittest.skipIf(unix_serve is None, 'install requirements-queue.txt for queue transport tests')
class QueueControlTests(unittest.TestCase):
    def server(self, reply):
        server = QueueServer(reply)
        self.addCleanup(server.close)
        return server

    def test_exact_wake_cleanup_uses_pagination_and_preserves_other_entries(self):
        def reply(connection, request):
            if request['method'] == 'thread/queue/delete':
                return {'id': request['id'], 'result': {'deleted': True}}
            if request['params'].get('cursor') is None:
                page = {'data': [{'id': 'other-task', 'input': [{'type': 'text', 'text': 'keep'}]}],
                        'nextCursor': 'page-2'}
            else:
                page = {'data': [{'id': 'owned-wake',
                                  'input': [{'type': 'text', 'text': 'recorded pointer'}]}],
                        'nextCursor': None}
            return {'id': request['id'], 'result': page}

        server = self.server(reply)
        with patch('queue_control.subprocess.Popen', side_effect=AssertionError('unexpected subprocess')):
            with self.assertRaisesRegex(RuntimeError, 'different content'):
                retire(server.remote, 'fixture-thread', {'queue_id': 'owned-wake', 'message': 'wrong'})
            self.assertEqual(retire(server.remote, 'fixture-thread',
                                    {'queue_id': 'owned-wake', 'message': 'recorded pointer'}), 'deleted')
            self.assertEqual(retire(server.remote, 'fixture-thread',
                                    {'queue_id': 'absent', 'message': 'anything'}), 'absent_or_started')
        deletions = [request for request in server.calls if request['method'] == 'thread/queue/delete']
        self.assertEqual(len(deletions), 1)
        self.assertEqual(deletions[0]['params'],
                         {'threadId': 'fixture-thread', 'queuedSubmissionId': 'owned-wake'})
        self.assertTrue({request['method'] for request in server.calls}.issubset(
            {'initialize', 'initialized', 'thread/queue/list', 'thread/queue/delete'}))

    def test_matching_response_ignores_notifications_and_other_response_ids(self):
        def reply(connection, request):
            connection.send(json.dumps({'method': 'status', 'params': {}}))
            connection.send(json.dumps({'id': request['id'] + 100, 'result': 'unrelated'}))
            return {'id': request['id'], 'result': 'matched'}

        server = self.server(reply)
        client = QueueControl(server.remote)
        try:
            self.assertEqual(client.call('fixture/probe', {}), 'matched')
        finally:
            client.close()
        client.close()
        self.assertTrue(server.closed.wait(timeout=5))

    def test_rpc_error_is_reported_once_and_connection_is_closed(self):
        server = self.server(lambda connection, request: {
            'id': request['id'], 'error': {'code': -32000, 'message': 'fixture refusal'},
        })
        client = QueueControl(server.remote)
        try:
            with self.assertRaisesRegex(RuntimeError, 'fixture refusal'):
                client.call('fixture/refuse', {})
        finally:
            client.close()
        self.assertEqual(sum(request['method'] == 'fixture/refuse' for request in server.calls), 1)
        self.assertTrue(server.closed.wait(timeout=5))

    def test_initialization_failure_closes_the_open_connection(self):
        server = self.server(lambda connection, request: None)
        server.initialization_error = {'code': -32000, 'message': 'initialization refused'}
        with self.assertRaisesRegex(RuntimeError, 'initialization refused'):
            QueueControl(server.remote)
        self.assertTrue(server.closed.wait(timeout=5))
        self.assertEqual([request['method'] for request in server.calls], ['initialize'])

    def test_timeout_does_not_retry_after_notifications_without_a_response(self):
        def reply(connection, request):
            for _ in range(10):
                connection.send(json.dumps({'method': 'status', 'params': {}}))
            return None

        server = self.server(reply)
        client = QueueControl(server.remote)
        # Initialization uses the normal budget; the fixture never answers this next request.
        client.timeout = 0.05
        try:
            with self.assertRaisesRegex(TimeoutError, 'timed out'):
                client.call('fixture/no-response', {})
        finally:
            client.timeout = 15
            client.close()
        self.assertEqual(sum(request['method'] == 'fixture/no-response' for request in server.calls), 1)
        self.assertTrue(server.closed.wait(timeout=5))

    def test_peer_closure_is_reported_without_reconnecting(self):
        def reply(connection, request):
            connection.close(code=1011, reason='fixture disconnected')
            return None

        server = self.server(reply)
        client = QueueControl(server.remote)
        try:
            with self.assertRaisesRegex(RuntimeError, 'connection failed'):
                client.call('fixture/disconnect', {})
        finally:
            client.close()
        self.assertEqual(sum(request['method'] == 'initialize' for request in server.calls), 1)

    def test_queue_pages_can_contain_inputs_larger_than_one_megabyte(self):
        text = 'x' * (1024 * 1024 + 128)
        server = self.server(lambda connection, request: {
            'id': request['id'], 'result': {
                'data': [{'id': 'long-input', 'input': [{'type': 'text', 'text': text}]}],
                'nextCursor': None,
            },
        })
        client = QueueControl(server.remote)
        try:
            entries = list(client.pending('fixture-thread'))
        finally:
            client.close()
        self.assertEqual(entries[0]['input'][0]['text'], text)


if __name__ == '__main__':
    unittest.main()
