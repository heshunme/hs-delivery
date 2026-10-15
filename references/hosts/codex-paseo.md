# Codex and Paseo host

Read with [session handoffs](../session-handoff.md), the [task inbox](../result-inbox.md) and [CI continuation](../ci-watcher.md). This adapter retains the source workflow's Codex/Paseo delivery path. Inspect destination tools and completion behavior before relying on them; the package does not establish compatibility with every Codex or Paseo version.

Follow [project initialization and recovery](../setup-and-recovery.md) before first adoption: inspect, preview actual changes and obtain setup confirmation. Append the recovery pointer to the applicable loaded `AGENTS.md` or an established project instruction mechanism, preserving its existing rules. Record the actual harness/version and local interpreter in the setup receipt; Codex, Paseo-managed sessions and other execution surfaces need their own capability checks. A pointer is intended to lead back to the skill and task card; distinguish writing it, observing it loaded and verifying compaction/resume in a later [host trial](../host-acceptance.md).

## Choose the actual mechanism

For persistent roles, prefer Paseo-managed Codex sessions with native `codex queue` handoffs when those capabilities are present. If unavailable but built-in collaboration is available, use independent subagents and their own messaging tools, and record that choice. Use fresh context for independent review. Collaboration identifiers are not native Codex thread UUIDs.

Built-in Codex subagents return through the assignment's hand-back variant; the queue-specific steps below do not apply. Their final answer reaches the parent's mailbox without starting an idle parent's new turn. Inside an active turn, mail can end a blocking wait early. A coordinator relying on them stays in its turn and blocks on one long, interruptible `clock.sleep` when the host exposes it and supports waking on mail, otherwise on `wait_agent` within that tool's duration limit. A round that must outlast the coordinator's turn belongs to a persistent Paseo session with an inbox. Do not assume a native completion notice supplies cross-turn continuation.

For persistent Paseo-managed sessions, use installed session-creation and activity tools. Record the Paseo agent ID, native Codex thread UUID, working directory and actual runtime owner separately. Keep one runtime owner per thread; enqueue without resuming that UUID under another owner. A matching title or directory does not enroll another session into the task. Use queue for routine follow-ups rather than a host prompt operation that can replace a busy run.

Read participant status or activity at a checkpoint, on a wakeup or when its expected-result observer reports, not on a timer. The observer carries that watch outside the model.

## Native queue handoffs

Before using queue, inspect `codex queue --help` and the local daemon's status via `codex app-server daemon version`. The Python adapter expects the latter to return JSON with `status: running` and `socketPath`. Its queue receipt parser expects `Queued message <uuid> for thread <uuid>`. If those contracts differ, report that the queue path is unavailable until the adapter is deliberately updated; do not change a Codex inbox to `harness` to mask the missing queue.

Check the installed endpoint's read-only queue protocol before depending on cleanup. `queue_control.py` connects directly through Python's `websockets` library and speaks JSON-RPC over a Unix WebSocket: `initialize`, `initialized`, `thread/queue/list`, `thread/queue/delete`. It bounds connection, request and close waits and does not reconnect or retry requests automatically. A local protocol test covers this adapter against a fixture, not a real host or its wakeup behavior.

For an authorized worker assignment, persist intent and its artifact before sending:

```text
codex queue --thread <registered-native-thread-uuid> --message <handoff-text>
```

Use structured subprocess arguments or proper shell quoting. Save the queued-submission receipt. Acceptance into a queue is not completion, loading or resumption. Busy targets may consume inputs only after their turn ends; name checkpoints when feedback must precede the next step. Do not replace a busy run merely to deliver routine feedback. Respect user stops and reconcile uncertain delivery before any retry; queue submission is not exactly-once.

## Inbox registration

Python 3.11+/fcntl, Git, installed `requirements-queue.txt` and compatible local Codex tools are prerequisites for this path. Use the interpreter with that dependency installed for inbox operations, result publishers and observers; launchers in other terminals need the same environment or its explicit interpreter path. The recipient must stay available in its original runtime. An explicit local Unix endpoint can be passed with `--remote unix:///absolute/socket`; otherwise registration pins the existing daemon endpoint.

`codex-queue` is the default inbox transport. `harness` is for hosts such as Claude Code that supply the required completion path, not the Codex/Paseo inbox path.

```text
python3 <skill>/scripts/task_inbox.py --mailbox <task-dir>/inbox init
  --task <task-id> --transport codex-queue --thread <coordinator-native-uuid>
```

Publication during active work only records results. The first result while waiting queues one shared inbox pointer. `take` attempts to retire only that inbox's saved queue ID after matching its exact content. It cannot recall input that already started. Preserve uncertain intents and receipts; do not clear a thread's whole queue or erase state to force a retry.

Retain the host's failure visibility where available. A completion subscription may cover only the initial turn or combine success and failure notices; do not disable combined notifications just to silence a duplicate success notice. Reconcile notices together without acknowledgment loops, and missing expected results at checkpoints and on resumption rather than assuming every queued round has a callback.

## Finite observers

Read [CI continuation](../ci-watcher.md) before using an observer. Codex background commands do not supply the coordinator's required completion callback. Run coordinator-owned long commands through `watch_cmd.py` and guard each expected Paseo inbox result with `watch_result.py`, so the model need not poll. Participant-owned commands remain in that participant's turn and checkout.

Start the expected-result observer after dispatching the round, naming the delivery ID for its next checkpoint. It reads the inbox and optionally a Paseo participant's status. Use `--agent` only if `paseo inspect <agent> --json` returns a compatible `Status` field, or omit it to observe only the deadline. It does not watch native subagent hand-backs; those use the in-turn waiting path above. A later stage gets a fresh observer binding for its own expected ID.

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
