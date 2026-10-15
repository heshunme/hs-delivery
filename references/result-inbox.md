# Result collection and wakeups

Use this for results returning to a coordinator that needs a ledger to be woken or to catch results no hand-back carries: results from Paseo-managed participants, and, alongside native hand-backs on either host, only publishers that keep working after publishing and CI observers. Claude Code participant rounds return through their hand-back trailer instead; see the [Claude host reference](hosts/claude-code.md#results). Work assignments to a worker still use the host's direct assignment mechanism. An inbox is a local file protocol, not a scheduler or a replacement thread owner. Do not fall back to queuing a separate input per result.

The inbox is a durable ledger of results and their dispositions. How a waiting coordinator is woken depends on its host and is fixed at registration:

| Transport | Coordinator host | Wakeup |
|---|---|---|
| `harness` (default) | A host with its own completion path, such as [Claude Code](hosts/claude-code.md) | The inbox sends nothing. Completion notices, when supported, come from the host. Otherwise consume results on explicit resumption. |
| `codex-queue` (explicit opt-in) | [Codex and Paseo](hosts/codex-paseo.md) with a verified compatible local queue | The first result after `wait` queues one pointer to the coordinator's Codex thread; later results share it. |

## Register once

When the task uses an inbox, register one per task and put its absolute path in every assignment that publishes to it:

```text
python3 <skill>/scripts/task_inbox.py --mailbox <task-dir>/inbox init
  --task <task-id> --transport harness
```

For queue wakeups, pass `--transport codex-queue --thread <coordinator-native-uuid>` instead. The host reference gives the prerequisites. An existing inbox is inspected, never reinitialized. The scripts require Python 3 on Linux, macOS or WSL (`fcntl`); native Windows support is not implemented. Keep inboxes local to the task; their absolute paths and host bindings are not a portable installation artifact.

## Publish every result; do not queue every result

Participants write immutable artifacts, then use:

```text
python3 <skill>/scripts/queue_result.py
  --mailbox <registered-inbox> --task <task-id>
  [--thread <registered-coordinator>] --delivery-id <sender-round-consumer>
  --sender <role> --artifact <absolute-result> --version <actual-version>
  --summary <short-result> --outbox <sender-outbox>
```

`--thread` is passed only to a `codex-queue` inbox and must match its registration. `recorded` means the result is durable. It does not mean a wakeup was sent or work was consumed. Each delivery ID binds its payload/hash permanently; changed content needs a new file and a new ID. Never edit a published artifact in place. When naming a commit, resolve the tested revision with Git in the actual candidate worktree; do not invent a full SHA from its prefix, and describe uncommitted inputs separately.

Do not additionally send a direct result, a READY acknowledgment, or create per-round host completion subscriptions. Treat any host notice as a hint to take the inbox, not a new assignment or a request for another reply. A local inbox cannot detect a worker that crashes before publishing; each host reference states what its notices cover. Keep missing-result recovery explicit. Finite CI observers publish their own error/deadline disposition.

For native background commands consumed directly by the coordinator, the host reference may use the command's exit, log and task record without an extra inbox publication. On a host without completion callbacks, `watch_cmd.py` publishes a long local command's exit and `watch_result.py` publishes a missing or overdue participant result; both share the CI observer's lifecycle (see the [Codex host reference](hosts/codex-paseo.md#finite-observers)).

## Coordinator: take, reconcile, acknowledge, then wait

At work resumption and at useful review/verification boundaries:

```text
python3 <skill>/scripts/task_inbox.py --mailbox <inbox> take
```

This marks the coordinator active and returns **all unprocessed results**, retiring any pending wakeup the transport owns. A callback for an empty batch needs no “already handled” commentary/final response and no reply to the sender.

Verify membership, artifact hash, version, actual findings and current required gates. Record a disposition for each result you have actually handled:

```text
python3 <skill>/scripts/task_inbox.py --mailbox <inbox> ack
  --delivery-id <exact-id> --sha256 <observed-artifact-hash>
  --disposition <fix/reuse/superseded/blocked conclusion and evidence>
```

Acknowledgment updates the local ledger; it sends no message. `take` does not mark results handled, and `ack` never acknowledges newer results implicitly. A superseded SHA can be acknowledged with that reason while retaining its historical outcome; it must not approve the new candidate.

If evidence is unusable, such as an overwritten or missing published file, explicitly invalidate that record instead of forcing an acknowledgment:

```text
python3 <skill>/scripts/task_inbox.py --mailbox <inbox> invalidate
  --delivery-id <bad-result-id> --sha256 <original-recorded-artifact-hash>
  --reason <why-the-claim-is-withdrawn> [--superseded-by <correction-id>]
```

This retains the original payload and records a reason and optional replacement in the same inbox. It removes only that entry from pending work; it neither approves the replacement nor satisfies a delivery gate. Review and acknowledge the correction separately. An identical invalidation can be retried while the inbox is open; an existing disposition cannot be rewritten. Use ordinary `ack` for intact historical evidence that has merely been superseded by a later candidate.

When no useful independent work remains, use:

```text
python3 <skill>/scripts/task_inbox.py --mailbox <inbox> wait
```

If it returns `ready: true`, results arrived during the work: process them before ending the turn. If it returns `mode: waiting`, end the current turn normally. Publishers and this transition share a file lock, so a result either appears in the ready batch or is retained for the transport's next wakeup. Do not end a waiting turn with the inbox still active, or put the model into repeated sleep/status polling. Ordinary short commands keep their normal completion path.

On deliberate task pause, use `pause` and stop owned observers as appropriate. `take`/`wait` cannot resume a paused task. `resume` is only for the user's authorized resumption; it returns to active, without automatically waking or running a model.

## Closeout

Publishers do not run while the machine is off, and an active coordinator that crashes before arming wait will not be woken automatically. Resume explicitly through the original host and `take` the retained results. The protocol does not override an interrupted or unloaded recipient's lifecycle.

Before delivery completion, `take` and dispose of remaining results, reconcile owned observers as the host reference describes, then `close`. Closure refuses unprocessed results or registered terminals without a recorded removal. New results cannot reopen a closed task. An observer's disappearance is resource cleanup, not successful CI: read the corresponding result/status, including crash, stop or uncertain notification, before asserting gate completion.
