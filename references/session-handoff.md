# Session setup and handoffs

Use this reference when arranging participants or handing off work under the [delivery skill's](../SKILL.md) task-scoped collaboration defaults or an explicit user request. The session mechanism, identifiers, delivery commands and notifications come from the coordinator's host: read [Codex and Paseo](hosts/codex-paseo.md) or [Claude Code](hosts/claude-code.md) alongside this page.

## Choose and initialize participants

Identify the coordinator's host and check which session-creation, status/activity and messaging tools are available before promising a particular mechanism. Use tool discovery when available, and record the mechanism chosen. If no independent participant can be created, disclose the independent-review gap and continue work that does not depend on it.

Create only the roles needed for the task, or explicitly bind an existing participant assigned to it. Write each assignment from the [templates](assignments.md). At creation, give each participant the actual goal, accepted decisions, repository guidance, candidate base/version, working directory, write boundary, completion condition, result location and next consumer. A bootstrap READY exchange is unnecessary for ordinary work. Participants inherit the task's scope, not authority to expand it or enroll unrelated sessions. The coordinator remains responsible for the user-facing conclusion.

If feedback must precede the next design-dependent or expensive step, name that checkpoint in the assignment. The participant publishes its stage result, states the next action, and ends that turn so pending feedback can reach it. At other useful boundaries, read shared task updates and continue ordinary implementation. Routine handoffs should not require canceling the worker; the host reference says how feedback reaches a busy participant.

Give an independent reviewer only the context needed to assess the change; use a fresh context rather than the implementer's full transcript where supported. Keep product-code writes with the designated implementer. Reviewer-owned findings and acceptance-owned evidence may be written separately. Dispatch review when the candidate is sufficiently stable to inspect, preferably before the first publication; review may overlap verification, but later edits require an impact assessment against the reviewed version.

Focused tests can write shared build or test caches even when the reviewer does not edit source. Serialize commands sharing those caches with the verification owner, or establish separate inputs and caches before running them in parallel. Another worktree alone does not prove cache isolation; ordinary file inspection can continue alongside tests.

Session creation and routine follow-ups inside the authorized task do not require repeated confirmation.

## Bind the task and recipient

Keep the task's participant mapping in its durable record: role, cwd and the identifiers the host reference names, each labelled with its namespace. Include the coordinator's identity as the return address, not only worker identities.

Read status and activity through the existing host when available. Finding another session in the same directory does not establish task membership or permission to send. An old participant mapping must be reconciled with the current task before reuse; do not wake a completed task merely because its title matches.

## Dispatch assignments once and observe

These steps apply to worker assignments. Results return through the host's result path, the hand-back trailer or the [task inbox](result-inbox.md), and the coordinator reconciles them in batches, however its host wakes it.

1. Write the assignment artifact before sending. Include observed code version, expected work, write boundaries and the return path. The input should point to the artifact rather than repeat the whole report.
2. Give the handoff a stable task/delivery ID and identify sender, role, recipient role, artifact location, observed version or content hash, and requested next action. Label it as an agent handoff within the user's existing task, not a new maintainer instruction.
3. Send it through the host's assignment mechanism, recording intent and receipt where the host reference asks for them. Acceptance by the transport is not recipient completion.
4. Confirm receipt and execution from the target's input/activity and corresponding completed turn or output artifact. Reconcile the result's code version and limits before moving the task forward.

No automatic retry loop or background model coordinator is installed by this skill. Use the task record to make pending work visible when the target is unavailable or delivery is uncertain. A finite [CI observer](ci-watcher.md) can publish a completion without repeatedly running the model.

## Return results for each round

For every assigned round, write an immutable result, then return it through the path the [assignment template](assignments.md) names: the hand-back trailer for participants whose final message reaches the coordinator natively, or `queue_result.py --mailbox ...` to the registered [task inbox](result-inbox.md) before ending the turn. Include the round, candidate, result and any blocked requirement. Use a distinct delivery ID for a distinct result. A `recorded` receipt proves durable publication, not that the coordinator was woken or handled it.

The coordinator reconciles results in batches at useful work boundaries: versions, exact IDs and hashes, a recorded disposition, and the card's `Expecting:` line. With an inbox it takes all pending results, acknowledges them locally and runs `wait` before ending an otherwise idle turn. Do not also send a direct result, a READY acknowledgment, or add per-round completion subscriptions. A host completion is a hint to reconcile the expected result, not an independent result or another assignment. Already handled or empty callbacks need no user-facing acknowledgment. What each host notifies, and what it misses, is in its host reference.

## Repeated or uncertain delivery

Keep the stable delivery ID in both the outbox entry and notification. Receivers check existing disposition and the artifact/code version before repeating a repair, validation, or onward notification. Sender-side intent/receipt files help prevent a blind second submission; they cannot prove delivery when a process stops between sending and saving its receipt.

For an uncertain send, inspect the target transcript, pending queue when accessible, and produced artifacts. Resolve that evidence first; neither a timeout nor an empty queue alone proves the message was lost. If a retry is justified, record that decision and preserve the same logical delivery ID for recipient recognition, without assuming the transport deduplicates it.

Completion messages should have a concrete next consumer. Avoid acknowledgment loops. The final coordinator updates the task record and reports completion rather than automatically sending the result around the same chain again.
