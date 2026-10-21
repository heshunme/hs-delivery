# Task records and handoffs

Use a record only when continuity across stages or sessions warrants one. Adapt the fields to the task; omit empty scaffolding. Keep one record at `.delivery/runs/<task>/task.md` unless the project already specifies a location: the task card on top as its only current state, then append-only history, linking existing plans, review reports, acceptance directories, and CI runs rather than moving or duplicating them.

## Task card

The top of `task.md` is a card of at most 20 lines between `<!-- task-card:start -->` and `<!-- task-card:end -->`. It is what a coordinator reads first after compaction or resumption, on either host, so it answers "what version, what is owed, who owes it, what waits on the maintainer" without the rest of the file. Write it only through the script, which replaces the whole block and stamps `Updated:`; it never needs the old text in context:

```text
python3 <skill>/scripts/task_card.py set --task-dir <task-dir> --card <file or ->
python3 <skill>/scripts/task_card.py show --task-dir <task-dir>
python3 <skill>/scripts/task_card.py list --runs <repo>/.delivery/runs
```

Use these lines; omit a line that has nothing to say:

```text
Status: active | paused | closed
Goal: <one line, link to the plan>
Stage: <current stage and the delivery endpoint>
Candidate: <code/artifact/config identity plus relevant inputs, or candidate set at absolute path>
Review: <actual reviewed inputs/reviewer; repair policy and remaining or writer-verified delta>
Rounds: <unit ID: used/limit; link unit scopes, interaction coverage, history and extensions>
Owners: writer=<id>, reviewer=<id>, verification=<id>, closeout=<id>
Expecting: <delivery IDs or background task IDs, each with its owner>
Grants: <applicable project or task grant IDs, or none>
Maintainer: <decisions waiting on the maintainer, or none>
Next: <next action and its owner>
Host: <coordinator host, inbox path if any>
```

Replace the card at every natural boundary: a round dispatched or returned, a candidate changed, a role moved, a decision made, closeout. Everything below it is append-only history and links; nothing there is edited in place to stay current, so updating the record never needs the old text in context.

## Authorizations

Keep a ledger section in `task.md` for grants that later participants need to recover, such as publishing, merging, releasing or deploying. Record each as `G<n>`: the maintainer's words verbatim, when they were said, the scope, conditions and expiry, with a pointer to its source. An expired or exhausted grant is marked so, not deleted. Actions relying on a grant name its ID in task history. This skill supplies no standing merge or publication grant; existing user instructions and applicable project authorization govern. Clarify a material ambiguity before the dependent action while continuing unblocked work.

## What the record captures

Capture enough for another session to continue without reconstructing the conversation. Each item has its short form on the card and its detail in an appended history entry or a linked file:

- **Goal and scope:** intended behavior, accepted plan, current stage, explicit exclusions and completion endpoint, such as a local result, reviewable PR/MR, authorized merge, versioned artifact or deployment stage.
- **Decisions:** the decision, its reason, and the user message or evidence that established it; distinguish proposals from accepted choices.
- **Version:** the [candidate inputs](#candidate-inputs-and-retention) relevant to each claim. For Git-backed work include branch, comparison base, candidate HEAD/tree and relevant staged, unstaged or untracked changes; identify private files instead of implying HEAD captures them. For a task spanning independent repositories, follow [multi-repository delivery](multi-repo.md): link a small candidate set from the card and keep each repository, external input, review and check tied to its actual version.
- **Responsibilities:** current code writer, independent reviewer, verification owner and closeout owner as applicable. Record the actual session mechanism, cwd and known session IDs; label the ID namespace, such as Paseo agent ID, native Codex thread ID, collaboration task path, Claude subagent ID or Claude background task ID. Unknown IDs remain unknown. Distinguish planned review, completed independent review and writer verification, with actual versions covered.
- **Review policy and rounds:** resolved severity/treatment/recheck policy and its source; each predeclared unit's scope, completion condition, interaction coverage and consumed/maximum rounds; each round's candidate and findings added/resolved/remaining; and the next justified action. Record any extension or scope-repartition decision; replacement, compaction, rebase and retroactive splitting do not reset counts. Reconstruct missing counts from assignments/results before dispatching, rather than treating them as zero. Link a unit table when it cannot fit the short card.
- **Acceptance and evidence:** meaningful scenarios, required checks and environments, execution owner and timing, status, tested version and evidence links. Determine conditional platform coverage from the project's rules; a focused job does not replace a broader required suite. Record failures, blocked checks and unexecuted cases explicitly. Existing evidence stays tied to its original version with any reuse rationale.
- **Findings and next action:** links to findings, confirmed severity, treatment/recheck decisions and evidence, the next responsible participant and any decision actually needed from the user. Confirmed blockers must be resolved before delivery completion; permitted major/minor deferments need reachable follow-ups, which may be private records. If monitoring is paused at the user's request, record who will resume and what result needs reconciliation.
- **Pending continuation, when used:** expected result, responsible participant and links to the registered inbox or observer binding. Keep message receipts and host resource state in those existing records. Waiting is pending work with an owner, not completed delivery; inspect the binding on resume.

The coordinator owns the card and the history. Contributors write their own finding or evidence files, then the coordinator links the result. This avoids competing edits to one status document. Replace the card at meaningful handoffs, scope decisions, verification results, and closeout, not after every command.

When helpers or observers are used, record their actual interpreter's absolute path with the task's host details. `.delivery/setup.md` can supply a previously selected environment to recheck, but does not establish availability in another worktree, terminal or machine. Setup receipts do not replace this task's session mapping or authorization ledger.

## Current state and historical evidence

Obsolete status is replaced on the card, never patched in the history. Keep history entries short and link existing result records; do not paste every handoff into `task.md`. Preserve each historical observation's version, environment, method and outcome. Add fixes, retests and corrections as linked later records, explaining any earlier method or conclusion that was wrong.

On a normal result or focused handoff, read the short card and relevant changes. Use explicit current-scope checks instead of auditing all historical artifacts and every linked checkout:

```text
python3 <skill>/scripts/task_card.py check-current --task-dir <task-dir>
  --inbox <registered-inbox> --pending-results
  --repo <repo> --worktree <assigned-candidate-checkout>
```

Select exact results with repeated `--result-id <id>` instead of `--pending-results`; add a candidate or evidence file with `--artifact <path> <expected-sha256>` when relevant. Choose the scope from the recorded candidate, owners and pending results. Inspect `checked`, `not_checked` and issues: unselected history, other worktrees, actual process liveness and product correctness are not established by this report. An anomaly or changed input may require expanding the selection. The command is read-only and does not ACK results or approve a gate.

At a broad stage boundary or closeout, use `task_card.py check --task-dir <task-dir> --repo <repo>` for the complete record/resource audit of one Git repository. Run it separately for every independent repository in a multi-repository candidate set, then reconcile the combined evidence. Inspect non-Git inputs and their records/resources directly as described in [closeout](closeout.md#resources-and-final-records); the Git helper does not validate them. A focused check does not replace the complete closeout audit.

Follow [closeout](closeout.md) for review carry-forward, actual merge order and final gate conditions. A failed repository inspection is an error; a linked checkout with `dirty: null` and an `error` has unknown state. Neither permits a clean-resource claim. The audit report itself does not approve delivery.

A coverage table can describe the current candidate if each row identifies its supporting version and any reuse rationale. A table labeled as acceptance of an earlier tree must keep that tree's actual methods and outcomes; later improvements belong in a new versioned entry. Raw failure evidence remains available after a passing retest.

## Candidate inputs and retention

Identify the inputs that can materially change the result being claimed, even for a single-repository task: code and local changes, relevant dependency/tool versions, configuration, dataset/model versions and the actual build or deployment artifact when applicable. Use existing lockfiles, manifests, immutable versions and retained artifacts; include only relevant inputs, not a new inventory system for every task. An unchanged Git SHA does not establish equivalence when a relevant non-code input changed. Keep secrets out of records; use an appropriate protected reference or non-secret version identifier.

Give each candidate one reliable source that reviewers and validation can reference. For source changes, use an available commit, or a base commit plus complete changes including added files and necessary metadata. For non-Git artifacts, use their actual version and retained source. When those cannot recover the tested inputs, retain a snapshot. A content hash verifies bytes; it cannot reconstruct missing files. Capture from stable inputs; concurrent writes or an unreadable Git state prevent a fixed/clean-candidate claim. Do not copy a full source tree merely because another review round or participant needs it.

Create runnable copies when stable inputs, isolated execution or remote deployment require them. Share their source identity across related results and reuse the existing manifest/checking tools. Record the relevant changed inputs rather than rebuilding a separate provenance system for each report.

Retain the result, method, environment, source identity and original evidence supporting important failures, fixes and remaining questions. Save unique failure databases, events and traces before cleanup, including cleanup in a runner's `finally` block; a watcher cannot recover files the command has already deleted. Keep actual build outputs when the conclusion depends on them. An archive failure does not erase an already recorded product observation, and neither replaces missing required evidence. Ordinary reproducible build intermediates, unpacked dependencies, generated load data and temporary profiles are execution resources; they do not all need permanent copies.

At closeout, confirm no active participant/process still uses a task-owned temporary directory and that needed evidence has a retained, reachable source before removing it. `task_card.py check --task-dir <task-dir> --repo <repo>` lists, read-only, the card state, every inbox's undisposed results, changed artifacts and unreconciled terminals, and every linked worktree of that repository still present, this task's or not, with its dirty or prunable state; invoke it once per independent repository when needed, while host background tasks are checked through the host. Keep unresolved diagnostic material and the input needed to reproduce it. Cleanup does not authorize removing unrelated files or bulk pruning old task archives. Store progress and corrections honestly even when disposable runtime data is reclaimed.

## Finding record

Use `<task-dir>/findings/<id>.md` when a finding needs a handoff. Include:

1. A stable finding ID, author, observed version, affected behavior, proposed/confirmed severity and current disposition. Use the [severity baseline](review-policy.md); record pending evidence separately from confirmed defects.
2. Preconditions: environment, fixture identity and state, and any relevant concurrent operation.
3. Exact actions, expected result, actual result, and supporting logs, screenshots, tests, or code references. Distinguish reproduction from inference.
4. Impact and reachability, requirement/source, resolution criterion, selected action and any accepted product decision. For a proposed blocker, explain which blocker condition holds; retain the coordinator's classification and treatment basis.
5. Resolution appended to the original observation: fixed candidate identity (SHA/local changes or relevant artifact/configuration version), retested scenarios, tested environment/version, results, remaining limits, and the project's required recheck outcome or its policy permitting writer verification only.

Keep evidence where the tool already saves it. Task-owned acceptance evidence can live at `<task-dir>/acceptance/evidence/`. References in the current record are enough; a second copy of every log is unnecessary.

## Notification pointer

Within the task's authorized collaboration, persist the finding first and return it through the assignment's result path, the hand-back trailer or the registered inbox (direct sends are for worker assignments), without requesting fresh permission for each routine handoff. A useful notification identifies the sender and role, task, finding ID, artifact path, observed SHA and requested next action. For separate worktrees, include the actual accessible artifact location instead of assuming ignored files exist in every checkout.

Keep agent handoffs distinguishable from new maintainer instructions; their scope comes from the assigned task. Do not infer that similarly titled sessions belong to it. The record is the durable handoff; sending a message does not itself confirm receipt or execution. Follow [session setup and handoffs](session-handoff.md) for the chosen transport and its observed lifecycle limits.
