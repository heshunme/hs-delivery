---
name: hs-delivery
description: Coordinate software delivery across implementation, independent review, acceptance and closeout. Use only when the user explicitly requests hs-delivery or continues a task for which they have already chosen it. Ordinary planning, local edits, standalone code review, and discussion or modification of this skill do not by themselves invoke it.
---

# HS Delivery

Keep the accepted task, implementation, findings and validation tied to the same scope and candidate inputs. Scale the workflow to the work; brief repairs can remain in one session. User instructions and applicable repository rules govern.

## Establish the project and task

Resolve the target repository separately from this skill's installation. Read its applicable `AGENTS.md` or equivalent instructions, then its existing task or planning entry point. If present, read `.delivery/delivery.md` for project-specific delivery conventions. The [project contract](references/project-contract.md) describes the information to recover and links a starter template; an existing project structure can supply it without a new file.

Inherit established project policy and valid grants with their sources; project choices override the general defaults. Use defaults for uncovered behavior without turning every empty field into a user decision. Resolve material conflicts or gaps affecting the current endpoint, and record authority separately. Missing configuration neither removes defaults nor creates a grant.

When project infrastructure is missing or incomplete, follow [setup and recovery](references/setup-and-recovery.md): inspect without writing and explain concrete changes; obtain confirmation for setup outside existing authorization. Reuse equivalent infrastructure and carry forward already authorized changes without asking again. Skill invocation alone does not authorize setup, and consultation or a brief task need not create persistent records. Approval to update this skill package does not initialize its repository or any other project.

For a request to continue a plan, recover the accepted goal, current stage, decisions and remaining work before choosing an implementation task. Check dated plans against current code and user instructions. An issue list or last completed PR does not establish the next milestone.

When one accepted task spans multiple independent Git repositories, read [multi-repository delivery](references/multi-repo.md). Resolve conflicting plan sources, choose one coordination record, classify each repository or external dependency, and pin the candidate set before assigning work. A non-Git aggregate directory is not a repository, and a passing member repository does not complete the combined delivery.

Reading another repository only for architecture, caller context or incidental comparison does not make the delivery multi-repository. Use this path only when another repository is a pinned write or verification unit, or supplies required versioned evidence for the accepted delivery.

Choose the requested mode:

- **Planning:** establish decisions and acceptance needs; commands in a plan do not start implementation.
- **Implementation or repair:** complete the authorized scope, carrying accepted decisions forward.
- **Review:** use the [review method](references/review-method.md) with the project's rules and preserve a review-only boundary. An explanatory walkthrough serves a different purpose from independent review.
- **Acceptance or closeout:** reconcile the candidate version with evidence and findings, then finish the authorized endpoint.

Derive commit, push, PR, merge, release and deployment authority from the user's request and applicable project grants. This skill grants none of those actions on its own and supplies no hook-bypass exemption. Record grants that later sessions need to recover in the [task record](references/task-record.md#authorizations).

On compaction or genuine context loss, reload this skill, applicable project policy and the active task card before acting. During ordinary continuation, consume changed inputs, decisions and pending results instead of repeatedly loading unchanged rules and full history. Put the recovery reminder in a loaded project instruction source outside the skill body; [setup and recovery](references/setup-and-recovery.md) separates written configuration, observed loading and verified recovery. Use `scripts/task_card.py list --runs <runs-dir>` and `show --task-dir <task-dir>` when the task uses these helpers. Historical completion claims apply to their recorded versions.

## Assign ownership and preserve independence

For substantial complete delivery, identify the writer, independent reviewer, expensive-verification owner and closeout owner, along with the delivery endpoint: a local result, PR/MR, merge, versioned artifact, release or deployment stage as applicable. Roles may share a session where independence is not needed. Full delivery normally includes independent review; disclose a gap if host capabilities or task restrictions prevent it, and continue unblocked work.

Before creating participants, read [session handoffs](references/session-handoff.md) and the applicable [Codex/Paseo](references/hosts/codex-paseo.md) or [Claude Code](references/hosts/claude-code.md) reference. Use the tools actually available. Give a reviewer fresh context containing the goal, accepted decisions, repository rules, candidate version and necessary artifacts rather than the implementer's full conversation.

Write assignments from the [templates](references/assignments.md), retaining their severity, review-budget, verification and hand-back rules when filling project parameters. Keep one code writer per checkout and one owner for expensive checks on shared resources. Review may overlap verification on stable inputs. The coordinator selects repairs after classifying findings; the writer verifies fixes and obtains the rechecks required by project policy. Apply [review coverage](references/closeout.md#review-coverage) to later changes without claiming unreviewed fixes were independently reviewed.

Make routine design and implementation choices within accepted scope and record their basis. For a difficult in-scope trade-off, seek fresh independent advice before deciding; resolve conflicting advice rather than alternating implementations. Escalate reversals of accepted decisions, substantial scope or behavior changes, and consequential security, cost or external effects not already authorized.

Set checkpoints when feedback must precede a design-dependent or expensive next step. Reconcile each new result before deciding whether another task is needed; suggestions are not automatic dispatch triggers. Recover a lost participant's artifacts before repeating work, following host and project recovery rules. Do not silently turn the coordinator's own inspection into independent review.

## Maintain a small durable record

Continue an existing task record. When work spans stages or sessions and has no established record, use `.delivery/runs/<task>/task.md` in the target project. Default `.delivery/` records are local and private; setup uses Git's local exclusion, preserving existing record conventions. Resolve `<skill>`, `<repo>`, `<task-dir>` and output paths to actual absolute locations in assignments; ignored project files may be absent from worktrees.

Follow [task records](references/task-record.md): a short current card at the top, then append-only history and links. Replace the card through `scripts/task_card.py`; contributors write their own immutable results. Keep original failures and add fix/retest evidence with its actual version.

Collect results through the coordinator host's result path. Paseo-managed Codex participants publish to the [task inbox](references/result-inbox.md), whose default `codex-queue` transport wakes a waiting coordinator: active work accumulates results without queued turns; take and reconcile them at useful boundaries, then arm waiting before ending a turn. Claude and built-in Codex subagents return through their native hand-back; add an inbox only for publishers that outlive that hand-back, following the host reference. Claude uses `--transport harness` explicitly for that inbox. Verify artifact hashes and versions, reconcile results in batches, and record a disposition for each result actually handled.

Report material findings, decisions, progress and blockers. Empty callbacks need no user-facing acknowledgment. In each handoff needing a maintainer decision, restate all pending choices with their options, recommendation, what they block and a concise reply format. Before the maintainer steps away or a long idle period, collect those questions together; turn scheduling-only questions into stated defaults the maintainer can veto. Explain which active participants depend on the session staying open, and record the recovery owner when it will close.

## Choose acceptance and checks before expensive work

For substantial behavior changes, define scenarios tied to accepted requirements, relevant inputs, environment and observable outcomes. Distinguish required conditions from engineering starting values and diagnostic observations. Use the [acceptance template](references/templates/acceptance.md) and [verification guidance](references/verification.md) to choose sufficient evidence and return to the delivery goal when research or tooling expands. Judge coverage by the affected behavior chain and applicable platforms, rather than test counts.

Recover the project's required gates and conditional platform checks at kickoff; revise applicability if scope changes. Record the owner and execution point. Probe needed local capability cheaply before declaring an environment unavailable. Required but unexecuted acceptance stays visible with a next owner.

Use the [verification budget](references/verification.md) to avoid duplicate full runs on the same inputs. Preserve required hooks and checks; project-specific commands and exemptions belong to the project contract. A skill-only edit needs relevant loading, structural and helper checks, scaled to the changes.

Reuse evidence only when its covered behavior and [relevant candidate inputs](references/task-record.md#candidate-inputs-and-retention) remain unchanged, including configuration, data or actual artifacts when material. Record the original tested version and why it still applies. A passing rerun alone does not explain an earlier failure.

## Carry findings through fixes

Give each finding a stable ID, observed version, triggering scenario, expected/actual behavior and reproducible evidence. Distinguish reproduction from inference and preserve fixture differences that affect reachability.

Use [finding severity and review convergence](references/review-policy.md). Confirmed blockers must be resolved; major/minor repair choices and whether fixes need independent rechecks follow project policy. Every finding needs a disposition; accepting or deferring an unresolved blocker does not complete the delivery. Keep missing evidence distinct from a proven defect and retain corrections without silently rewriting history.

Default to one full review and at most two incremental rechecks per predeclared review unit. Establish unit scope and interaction coverage before dispatch; preserve consumed budgets across participants and sessions, without resets through renaming or retroactive splitting. Close review when blockers are resolved, project-required rechecks/checks hold and other findings have permitted dispositions; suggestions alone do not require more work. At the limit, stop automatic repair/review dispatch for that unit and reconcile remaining requirements with the maintainer. Budget exhaustion is not success.

Before publication, inspect changed comments, test names and documentation for accuracy and private planning vocabulary. Use the [comment-audit template](references/templates/comment-audit.md) for a focused pass when the project requires it or the change warrants one; a separate audit's triggers, independence, scope and execution point are project policy.

## Wait through the host's supported completion path

For an otherwise idle CI wait, read [CI continuation](references/ci-watcher.md) and use the host's completion path: the finite observer for Codex/Paseo, or native background completion where supported. Record the pending gate and continuation owner before ending a waiting turn; this is not delivery completion. Observers never approve, merge, publish or deploy.

When an inbox is used, `take` and reconcile results, then `wait` before ending an idle turn. If it reports a ready batch, process it first. Do not replace missing completion support with model sleep/status loops or promise wakeups the host cannot provide. Record a responsible next action when explicit resumption is needed.

The same applies to any wait longer than a few minutes. On a host without completion callbacks, run coordinator-owned long local commands through `watch_cmd.py` and guard each expected inbox result with `watch_result.py`, following the [Codex host reference](references/hosts/codex-paseo.md#finite-observers). These observers carry monitoring outside the model. Check once that the installed commands and flags work, and retain stderr and exit status. A participant's own commands remain in its assigned turn and checkout.

## Reconcile the endpoint

Before claiming completion, follow [closeout](references/closeout.md) to compare the candidate with review coverage, finding dispositions, applicable checks, CI and actual acceptance. Distinguish the authorized endpoint from later publication or rollout stages. State any remaining requirement and owner. For multiple PRs/MRs, validate the actual merge order and recheck remaining candidates as their base changes.

When merging is authorized, initial review and the project's repair recheck policy must be satisfied for the current candidate, all confirmed blockers resolved, required checks passed on applicable inputs, and other findings disposed of. No merge-blocking maintainer decision or hold may remain. Report actual reviewed versions and any fixes verified without independent recheck. Use an exact-head guard where the platform provides one. A successful observer result applies only to its pinned inputs.

Preserve necessary evidence, reconcile owned observers and host resources, dispose of inbox results and close registered inboxes. For Git-backed inputs, run `scripts/task_card.py check --task-dir <task-dir> --repo <repo>` to inspect record debts, separately for every independent repository in a multi-repository task. Reconcile non-Git inputs and resources directly; the Git helper does not validate them. Then use host tools for processes and background tasks. Inspection errors or unknown checkout state require reconciliation; an empty or incomplete report is not a successful gate. A disappeared process proves cleanup rather than a successful check. Set the task card to `Status: closed` last, and reclaim only task-owned execution resources whose needed evidence is retained.
