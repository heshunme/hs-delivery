// Exercise the packaged bridge from an unrelated cwd against a disposable Unix fixture.
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const fs = require('node:fs/promises');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');
const { WebSocketServer } = require('ws');

test('queue cleanup only removes the exact saved ID and text', { timeout: 15000 }, async (t) => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'hs-queue-'));
  const socket = path.join(directory, 'queue.sock');
  const server = http.createServer();
  const websocket = new WebSocketServer({ server });
  t.after(async () => {
    for (const client of websocket.clients) client.terminate();
    await new Promise((resolve) => websocket.close(resolve));
    await new Promise((resolve) => server.close(resolve));
    await fs.rm(directory, { recursive: true, force: true });
  });
  const calls = [];
  const entries = [
    { id: 'another-task', input: [{ type: 'text', text: 'leave this alone' }] },
    { id: 'owned-wake', input: [{ type: 'text', text: 'recorded pointer' }] },
  ];
  websocket.on('connection', (client) => {
    client.on('message', (bytes) => {
      const request = JSON.parse(bytes.toString());
      calls.push(request);
      if (request.id === undefined) return;
      let result = {};
      if (request.method === 'thread/queue/list') result = { data: entries, nextCursor: null };
      if (request.method === 'thread/queue/delete') result = { deleted: true };
      client.send(JSON.stringify({ id: request.id, result }));
    });
  });
  server.listen(socket);
  await once(server, 'listening');

  const scripts = path.resolve(__dirname, '../scripts');
  const program = [
    'import sys',
    'sys.path.insert(0, sys.argv[1])',
    'from queue_control import retire',
    'endpoint = "unix://" + sys.argv[2]',
    'try:',
    '    retire(endpoint, "fixture-thread", {"queue_id": "owned-wake", "message": "wrong text"})',
    'except RuntimeError:',
    '    pass',
    'else:',
    '    raise AssertionError("mismatched wake was accepted")',
    'assert retire(endpoint, "fixture-thread", {"queue_id": "owned-wake", "message": "recorded pointer"}) == "deleted"',
    'assert retire(endpoint, "fixture-thread", {"queue_id": "absent", "message": "anything"}) == "absent_or_started"',
  ].join('\n');
  const child = spawn('python3', ['-c', program, scripts, socket], { cwd: directory });
  t.after(() => { if (child.exitCode === null) child.kill('SIGKILL'); });
  let diagnostics = '';
  child.stderr.on('data', (bytes) => { diagnostics += bytes; });
  const [code] = await once(child, 'close');
  assert.equal(code, 0, diagnostics);
  const deletions = calls.filter((request) => request.method === 'thread/queue/delete');
  assert.equal(deletions.length, 1);
  assert.deepEqual(deletions[0].params, { threadId: 'fixture-thread', queuedSubmissionId: 'owned-wake' });
});
