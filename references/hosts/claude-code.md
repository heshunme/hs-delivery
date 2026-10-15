# Claude Code host

Read with [session handoffs](../session-handoff.md), [assignments](../assignments.md) and [CI continuation](../ci-watcher.md). Use the destination host's actual tool names and capabilities. Private validation reports from the source project are not part of this package.

## Participants and feedback

When available, create fresh background subagents with `Agent` and record the returned IDs. Use `SendMessage` or the installed equivalent for later rounds. Avoid a fork carrying the implementer's full transcript for independent review. Roles that need continuity should retain their own session between rounds.

Keep one writer per checkout. If the host supplies worktree isolation, use that worktree rather than creating another inside it. Ignored plans, task records and this installed skill may be absent there; assignments give actual accessible absolute paths. Reconcile changed worktrees into the candidate and reclaim owned temporary resources at closeout.

A participant's file access may be broader than its assignment. State write boundaries explicitly. Keep code review read-only on product files and serialize commands sharing mutable caches with the verification owner.

Deliver feedback through the supported messaging mechanism without stopping useful work. If the next step depends on feedback, name the checkpoint where the participant publishes a result and ends that round. Check installed busy-message behavior rather than assuming delivery timing.

## Results

Use the assignment's native hand-back trailer by default. The immutable artifact is the result of record; completion text is a claim to verify. Check its hash, version and task membership, record the disposition and update the task card's expected work.

A completion notice alone may describe interim work. If the round is still running, keep it pending. If it has ended without a usable artifact/trailer, resume it for correction or record the missing result. Avoid acknowledgment loops.

Register a `harness` inbox only for stage publishers that keep working or observers whose result is not carried by the participant's final hand-back:

```text
python3 <skill>/scripts/task_inbox.py --mailbox <task-dir>/inbox init
  --task <task-id> --transport harness
```

Publishers omit `--thread`. This ledger sends nothing; the host must supply completion. A result from an unrelated process can remain pending until the next explicit callback or resumption. If an inbox exists, take its batch on useful callbacks and run `wait` before ending an idle turn.

## Long commands and CI

If native background Bash supplies completion callbacks, it is a suitable path for waiting on an authorized CI run. Verify installed CLI usage first, then retain the expected SHA/run identity, log path, background task ID and command exit:

```text
gh run watch <run-id> --repo <owner/repo> --exit-status --interval 60
```

After callback, reconcile fresh PR/run identity and required checks. No extra inbox wrapper is needed for a command consumed directly by the coordinator. A failed wait leaves the gate open. A process disappearing does not establish a successful CI result.

`watch_ci.py` is optional when structured state or durable publication is useful. Launch through native background Bash with an `exec` launcher so signals reach Python. Use a registered harness inbox, omit `--thread`, and confirm `ready.json` with current process state before promising continuation.

On callback, read the command exit, binding and status before taking results. `recorded` means publication; `stopped` means no success claim; a nonzero exit, `notification_uncertain`, missing state or mismatched binding leaves a requirement to reconcile. If the observer ended without a result, resolve the open gate from fresh external state or a new explicit observer binding in the same turn where possible.

Stop obsolete owned commands through their actual background IDs. Reconcile final process state and preserve logs. This host need not use the Paseo terminal ledger. Session exit may end subagents and commands without a callback; do not assume they survive or silently redispatch completed work on resumption.
