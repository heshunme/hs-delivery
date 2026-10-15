// The optional queue transport resolves its dependency from this skill's installation.
const net = require('node:net');
const readline = require('node:readline');
const WebSocket = require('ws');
const connection = new WebSocket('ws://localhost/', {
  createConnection: () => net.createConnection(process.argv[2]),
  handshakeTimeout: 10000,
});
const pending = [];
const input = readline.createInterface({ input: process.stdin });
input.on('line', line => {
  if (connection.readyState === WebSocket.OPEN) connection.send(line);
  else pending.push(line);
});
connection.on('open', () => {
  for (const line of pending) connection.send(line);
  pending.length = 0;
});
connection.on('message', data => process.stdout.write(`${data.toString()}\n`));
connection.on('error', error => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});
connection.on('close', () => process.exit(process.exitCode || 0));
input.on('close', () => connection.close());
process.on('SIGTERM', () => { connection.terminate(); process.exit(0); });
