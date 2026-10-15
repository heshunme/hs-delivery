# Codex and Paseo host

Read with [session handoffs](../session-handoff.md) and, when needed, the [task inbox](../result-inbox.md). This is an optional host adapter extracted from a particular installation. Inspect destination tools and completion behavior before relying on them; the package does not establish compatibility with every Codex or Paseo version.

## Choose the actual mechanism

Use native collaboration tools for roles that fit their lifecycle. Record returned collaboration identifiers and use that host's message/follow-up tools. Native IDs are not Codex thread UUIDs. Use fresh context for independent review. Determine whether the host wakes an idle parent on completion; if results arrive only within an active turn, wait through the supported in-turn completion tool. Work that must outlive that turn needs a verified persistent session path or explicit later resumption.

For persistent Paseo-managed sessions, use installed session-creation and activity tools. Record the Paseo agent ID, native Codex thread UUID, working directory and actual runtime owner separately. Keep one runtime owner per thread. A matching title or directory does not enroll another session into the task.

## Optional native queue

Before opting in, inspect `codex queue --help` and the local daemon's status via `codex app-server daemon version`. The Python adapter expects the latter to return JSON with `status: running` and `socketPath`. Its queue receipt parser expects `Queued message <uuid> for thread <uuid>`. If those contracts differ, use native hand-backs or a non-sending ledger until the adapter is deliberately updated.

Check the installed endpoint's read-only queue protocol before depending on cleanup. The bundled bridge speaks JSON-RPC over a Unix WebSocket: `initialize`, `initialized`, `thread/queue/list`, `thread/queue/delete`. It loads `ws` from this skill's own dependency installation. A local protocol test covers this adapter against a fixture, not a real host or its wakeup behavior.

For an authorized worker assignment, persist intent and its artifact before sending:

```text
codex queue --thread <registered-native-thread-uuid> --message <handoff-text>
```

Use structured subprocess arguments or proper shell quoting. Save the queued-submission receipt. Acceptance into a queue is not completion, loading or resumption. Busy targets may consume inputs only after their turn ends; name checkpoints when feedback must precede the next step. Do not replace a busy run merely to deliver routine feedback. Respect user stops and reconcile uncertain delivery before any retry; queue submission is not exactly-once.

## Inbox registration

Python 3/fcntl, Git, Node.js, installed `ws` and compatible local Codex tools are prerequisites for this path. The recipient must stay available in its original runtime. An explicit local Unix endpoint can be passed with `--remote unix:///absolute/socket`; otherwise registration pins the existing daemon endpoint.

```text
python3 <skill>/scripts/task_inbox.py --mailbox <task-dir>/inbox init
  --task <task-id> --transport codex-queue --thread <coordinator-native-uuid>
```

Publication during active work only records results. The first result while waiting queues one shared inbox pointer. `take` attempts to retire only that inbox's saved queue ID after matching its exact content. It cannot recall input that already started. Preserve uncertain intents and receipts; do not clear a thread's whole queue or erase state to force a retry.

Retain the host's failure visibility where available. A completion subscription may cover only the initial turn or combine success and failure notices. Reconcile missing expected results at checkpoints and on resumption rather than assuming every queued round has a callback.

## Finite observers

Read [CI continuation](../ci-watcher.md) before using an observer. `watch_cmd.py` runs a coordinator-owned long command; `watch_result.py` guards one expected inbox delivery and optionally checks a Paseo participant's status. Use the latter only if `paseo inspect <agent> --json` returns a compatible `Status` field, or omit `--agent` to observe only the deadline.

Launch observers only through an available mechanism whose lifetime and completion path are understood. For Paseo, create a dedicated terminal, register its actual UUID, then send `exec python3 ...` through the host terminal tool. A literal carriage return submits the command on hosts using terminal key input. Long commands can use a task-owned launcher and `exec bash <launcher>`.

```text
python3 <skill>/scripts/task_inbox.py --mailbox <inbox> terminal-add
  --terminal-id <terminal-uuid> --state-dir <observer-state-dir>

exec python3 <skill>/scripts/watch_cmd.py --task <task-id> --label <name>
  --cwd <worktree> --state-dir <new-state-dir> --max-wait 7200
  --mailbox <inbox> --thread <coordinator-native-uuid>
  -- <actual-command-and-arguments>

exec python3 <skill>/scripts/watch_result.py --task <task-id>
  --expect <assigned-delivery-id> --version <assigned-version> --max-wait 7200
  --state-dir <new-state-dir> --mailbox <inbox> --thread <coordinator-native-uuid>
  [--agent <paseo-agent-id>]
```

Confirm readiness together with current process state. Before ending an idle turn, `wait` the inbox. Observers need no model-driven status loop. If no durable launch or wakeup path exists, retain an explicit next action instead of promising automatic continuation.

The command observer records Git state before/after, its exit and `command.log`. A dirty flag does not reconstruct local inputs; retain the necessary changes separately. A stop/deadline terminates its process group. The result observer exits without a second publication when the expected ID arrives; `missing` or `overdue` prompts investigation rather than automatic reassignment.

Stop through `STOP` or the verified owned process. After exit, preserve status and reconcile the dedicated terminal. For the bundled Paseo terminal ledger, save the host's full terminal list as `{"scope":"all","captured_at":"<current ISO timestamp>","terminals":[...]}` and run `terminals-reconcile --snapshot <file>`. The snapshot must follow registration and be at most 60 seconds old. Close a remaining owned terminal through the host and capture a new snapshot; do not touch unrelated terminals.

No observer survives arbitrary machine/session loss by guarantee. On resumption, inspect bindings, results, inbox and fresh external state. Merging remains a coordinator action under the current task's actual authorization.
