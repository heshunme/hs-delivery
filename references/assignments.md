# Assignments

Write every participant assignment from a template under `templates/`, filling its `<…>` fields, and save it as `<task-dir>/assignments/<delivery-id>.md` before sending. By default `<task-dir>` is `<repo>/.delivery/runs/<task>`. The templates carry the rules a worker needs on either host, so a coordinator that has lost the skill text to compaction still hands them on. Change a template when a rule changes; do not patch a rule into one task's assignment only.

| Template | Role |
|---|---|
| [implementer](templates/implementer.md) | sole writer of one worktree for one round |
| [reviewer](templates/reviewer.md) | independent code or design review, read-only on product code |
| [acceptance](templates/acceptance.md) | real-host or real-environment scenarios |
| [comment audit](templates/comment-audit.md) | independent text audit at the project's configured checkpoint |

## Filling a template

- Point to the design, decisions and earlier results by path instead of pasting them. An assignment states scope, base, write boundary, checks, checkpoint and return; it is not where the coordinator restates the design.
- Keep the templates' explicit severity, round-budget, verification, version and hand-back rules when substituting project commands. Supply the resolved project repair/recheck policy, predeclared review unit and its used/maximum rounds. Candidate identity includes relevant non-code inputs, not only a SHA. A link to the general skill alone does not carry those rules into a fresh worker's context.
- Keep the **Return** variant that matches the participant and delete the other. Participants whose final message reaches the coordinator natively, Claude subagents and Codex built-in subagents, end with the hand-back trailer. Paseo-managed sessions publish through `queue_result.py` to the registered inbox. A native participant that publishes stage results and keeps working keeps both: the inbox for stages, the trailer for its final hand-back. The [Claude](hosts/claude-code.md) and [Codex](hosts/codex-paseo.md) host references say which applies.
- Delivery IDs are filename-safe: letters, digits, `.`, `_` and `-`, no slashes.
- Name the checkpoint at which the worker publishes and ends its turn whenever feedback must precede the next step. On Codex a queued message reaches a busy worker only when its turn ends, so a long round without checkpoints can only be interrupted, not corrected.
- A normal follow-up for the same participant is a short delta assignment: changed inputs, selected work, current policy/counts, checkpoint and return address, linking unchanged rules and prior results. Do not repeat full reports or task history. After genuine context loss, or for a fresh/replacement participant, restore applicable rules and accessible inputs; a reference hash alone does not restore their contents.

Read [the review method](review-method.md) when assigning review and [severity and convergence](review-policy.md) before selecting repairs or another round. Reconcile returned evidence and findings before dispatching. Create another assignment when a new responsibility, feedback decision, fixed candidate or expensive-resource handoff needs a boundary; otherwise allow already authorized work to continue. Dispatch only selected findings; a reviewer report is not a blanket repair order. Later reviews cover the fixes, delta and affected interactions. Do not schedule a review solely because a new result arrived, a minor suggestion exists or a writer-verified repair satisfies project policy without independent recheck.

Before the first review dispatch, record unit scopes, completion conditions, interaction coverage and finite budgets using [convergence rules](review-policy.md#bound-the-review-cycle). Record each coordinated round against its unit at dispatch. At that unit's limit, reconcile remaining requirements before further automatic repair/review dispatch. Pass the existing unit/count to replacement participants; a new session, renamed task or retroactive split does not begin a new budget.

## Hand-backs

A worker's final message is a summary of at most about 1,500 characters: verdict, version, decisions needed and artifact paths. Detail belongs in the artifact. The artifact is immutable once returned; a correction is a new file and a new delivery ID.

## Splitting and refreshing participants

Split work across participants through the coordinator, each with its own worktree and assignment. A participant does not fork itself into a shared worktree: the fork inherits the parent's whole context and both write the same tree.

Consider a fresh implementer at a substantial responsibility or candidate boundary, passing the task card, relevant rules and latest result. Compaction alone does not require replacement. For abnormal interruption, first follow the host and project's session recovery rules and reconcile partial side effects; replace only when recovery is unavailable or a normal handoff calls for it. The coordinator does not turn its own inspection into the lost participant's independent review.
