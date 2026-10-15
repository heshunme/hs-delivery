# Assignments

Write every participant assignment from a template under `templates/`, filling its `<…>` fields, and save it as `<task-dir>/assignments/<delivery-id>.md` before sending. By default `<task-dir>` is `<repo>/.delivery/runs/<task>`. The templates carry the rules a worker needs on either host, so a coordinator that has lost the skill text to compaction still hands them on. Change a template when a rule changes; do not patch a rule into one task's assignment only.

| Template | Role |
|---|---|
| [implementer](templates/implementer.md) | sole writer of one worktree for one round |
| [reviewer](templates/reviewer.md) | independent code or design review, read-only on product code |
| [acceptance](templates/acceptance.md) | real-host or real-environment scenarios |
| [comment audit](templates/comment-audit.md) | pre-PR audit of every changed comment |

## Filling a template

- Point to the design, decisions and earlier results by path instead of pasting them. An assignment states scope, base, write boundary, checks, checkpoint and return; it is not where the coordinator restates the design.
- Keep the **Return** variant that matches the participant and delete the other. Participants whose final message reaches the coordinator natively, Claude subagents and Codex built-in subagents, end with the hand-back trailer. Paseo-managed sessions publish through `queue_result.py` to the registered inbox. A native participant that publishes stage results and keeps working keeps both: the inbox for stages, the trailer for its final hand-back. The [Claude](hosts/claude-code.md) and [Codex](hosts/codex-paseo.md) host references say which applies.
- Delivery IDs are filename-safe: letters, digits, `.`, `_` and `-`, no slashes.
- Name the checkpoint at which the worker publishes and ends its turn whenever feedback must precede the next step. On Codex a queued message reaches a busy worker only when its turn ends, so a long round without checkpoints can only be interrupted, not corrected.
- A later round is a short delta assignment that names the previous one; it does not repeat unchanged rules.

## Hand-backs

A worker's final message is a summary of at most about 1,500 characters: verdict, version, decisions needed and artifact paths. Detail belongs in the artifact. The artifact is immutable once returned; a correction is a new file and a new delivery ID.

## Splitting and refreshing participants

Split work across participants through the coordinator, each with its own worktree and assignment. A participant does not fork itself into a shared worktree: the fork inherits the parent's whole context and both write the same tree.

Replace a long-lived implementer with a fresh one at a natural boundary, such as a rebase onto new main, a merged predecessor, or after the participant's own context has compacted: hand the new one the task card and the latest result. The coordinator does not take over implementation or review in its own context when a participant is lost; it assigns a replacement.
