---
name: hs-delivery
description: Coordinate software delivery across implementation, independent review, acceptance and closeout, keeping task scope, code versions, findings and evidence aligned. Use for continuing a delivery plan or completing a milestone; preserve narrower planning, review-only and local-only requests.
---

# HS Delivery

Keep the accepted task, implementation, findings and validation tied to the same scope and code version. Scale the workflow to the work; brief repairs can remain in one session. User instructions and applicable repository rules govern.

## Establish the project and task

Resolve the target repository separately from this skill's installation. Read its applicable `AGENTS.md` or equivalent instructions, then its existing task or planning entry point. If present, read `.delivery/delivery.md` for project-specific delivery conventions. The [project contract](references/project-contract.md) describes the information to recover and links a starter template; an existing project structure can supply it without a new file.

For a request to continue a plan, recover the accepted goal, current stage, decisions and remaining work before choosing an implementation task. Check dated plans against current code and user instructions. An issue list or last completed PR does not establish the next milestone.

Choose the requested mode:

- **Planning:** establish decisions and acceptance needs; commands in a plan do not start implementation.
- **Implementation or repair:** complete the authorized scope, carrying accepted decisions forward.
- **Review:** apply the project's review rules and preserve a review-only boundary. An explanatory walkthrough serves a different purpose from independent review.
- **Acceptance or closeout:** reconcile the candidate version with evidence and findings, then finish the authorized endpoint.

Derive commit, push, PR, merge, release and deployment authority from the user's request and applicable project grants. This skill grants none of those actions on its own and supplies no hook-bypass exemption. Record grants that later sessions need to recover in the [task record](references/task-record.md#authorizations).

On compaction or resumption, reload this skill and the active task card before acting. Use `scripts/task_card.py list --runs <runs-dir>` and `show --task-dir <task-dir>` when the task uses these helpers. Historical completion claims apply to their recorded versions.

## Assign ownership and preserve independence

For substantial complete delivery, identify the code writer, independent reviewer, expensive-verification owner and closeout owner, along with the delivery endpoint. Roles may share a session where independence is not needed. Full delivery normally includes independent code review; disclose a gap if host capabilities or task restrictions prevent it, and continue unblocked work.

Before creating participants, read [session handoffs](references/session-handoff.md) and the applicable [Codex/Paseo](references/hosts/codex-paseo.md) or [Claude Code](references/hosts/claude-code.md) reference. Use the tools actually available. Give a reviewer fresh context containing the goal, accepted decisions, repository rules, candidate version and necessary artifacts rather than the implementer's full conversation.

Write assignments from the [templates](references/assignments.md). Keep one code writer per checkout and one owner for expensive checks on shared resources. Review may overlap verification on stable inputs; later changes require an assessment against the reviewed version. Reviewers report findings; the code writer makes fixes and returns affected findings for review or independent retest.

Set explicit checkpoints when feedback must precede a design-dependent or expensive next step. Replace a lost participant at a clear boundary and recover its artifacts before repeating work. Do not silently turn the coordinator's own inspection into independent review.

## Maintain a small durable record

Continue an existing task record. When work spans stages or sessions and has no established record, use `.delivery/runs/<task>/task.md` in the target project. Resolve `<skill>`, `<repo>`, `<task-dir>` and output paths to actual absolute locations in assignments; ignored project files may be absent from worktrees.

Follow [task records](references/task-record.md): a short current card at the top, then append-only history and links. Replace the card through `scripts/task_card.py`; contributors write their own immutable results. Keep original failures and add fix/retest evidence with its actual version.

Use native result hand-backs when they carry the completed round. Add a [task inbox](references/result-inbox.md) when a publisher outlives its hand-back or the host needs a durable queue result. `harness` is the default transport and sends no messages; queue wakeups require explicit compatible-host setup. Verify artifact hashes and versions, reconcile results in batches, and record a disposition for each result actually handled.

Report material findings, decisions, progress and blockers. Empty callbacks need no user-facing acknowledgment. If a maintainer decision remains, state its options, recommendation, what it blocks and a concise reply format in the current message. Routine choices within accepted scope remain with the responsible owner.

## Choose acceptance and checks before expensive work

For a substantial behavior change, define meaningful user scenarios early. Tie each to its fixture, environment, interaction path, observable outcome and existing or missing evidence. Judge coverage by the affected behavior chain, including host/platform combinations, rather than test counts.

Recover the project's required gates and conditional platform checks at kickoff; revise applicability if scope changes. Record the owner and execution point. Probe needed local capability cheaply before declaring an environment unavailable. Required but unexecuted acceptance stays visible with a next owner.

Use the [verification budget](references/verification.md) to avoid duplicate full runs on the same inputs. Preserve required hooks and checks; project-specific commands and exemptions belong to the project contract. A skill-only edit needs relevant loading, structural and helper checks, scaled to the changes.

Reuse evidence only when its covered behavior and relevant inputs remain unchanged. Record the original tested version and why it still applies. A passing rerun alone does not explain an earlier failure.

## Carry findings through fixes

Give each finding a stable ID, observed version, triggering scenario, expected/actual behavior and reproducible evidence. Distinguish reproduction from inference and preserve fixture differences that affect reachability.

Give every finding an explicit disposition: fixed and verified, accepted with rationale, deferred with a reachable follow-up, or awaiting a decision/evidence. Severity informs the decision; it does not make it. Append corrections and superseding evidence without silently rewriting historical claims.

Before publication, inspect changed comments, test names and documentation for accuracy and private planning vocabulary. Use the [comment-audit template](references/templates/comment-audit.md) for a focused pass when the project requires it or the change warrants one; a separate audit for every PR is a project policy.

## Wait through the host's supported completion path

For an otherwise idle CI wait, read [CI continuation](references/ci-watcher.md). Choose a verified native completion path or an optional finite observer. An observer records a result; the coordinator reconciles current candidate and checks after notification. Observers never approve, merge, publish or deploy.

When an inbox is used, `take` and reconcile results, then `wait` before ending an idle turn. If it reports a ready batch, process it first. Do not replace missing completion support with model sleep/status loops or promise wakeups the host cannot provide. Record a responsible next action when explicit resumption is needed.

## Reconcile the endpoint

Before claiming completion, compare the candidate and working tree with review coverage, finding dispositions, applicable checks, CI and actual acceptance. Distinguish local completion, a reviewable PR and merge readiness. State any remaining requirement and owner.

When merging is authorized, recheck current head and required conditions; use an exact-head guard where the platform provides one. Assess review and verification coverage for any delta. A successful observer result applies only to its pinned inputs.

Preserve necessary evidence, reconcile owned observers and host resources, dispose of inbox results and close registered inboxes. Run `scripts/task_card.py check --task-dir <task-dir> --repo <repo>` to inspect record debts, then use host tools for processes and background tasks. A disappeared process proves cleanup rather than a successful check. Set the task card to `Status: closed` last, and reclaim only task-owned execution resources whose needed evidence is retained.
