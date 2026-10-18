# Review coverage and delivery closeout

Read this when a reviewed candidate changes, when preparing publication/merge or when closing a delivery task. Project-specific gates and permissions still come from the actual task and project rules.

## Review coverage

Record the independent review's actual [candidate inputs](task-record.md#candidate-inputs-and-retention), including full SHA and local changes for Git-backed code. Compare them with the current candidate and inspect the full delta, including relevant configuration, data, dependencies, build artifacts, generated files and executable tests. Unchanged code alone does not carry evidence across changed non-code inputs.

- **Selected finding repairs:** apply the resolved project policy from [severity and convergence](review-policy.md#decide-treatment-before-dispatch). A fix always needs verification; independent recheck is required only when that policy requires it. Record the finding IDs, fix version, verification and policy source. A writer-verified fix may meet project completion conditions without extending the independent review's actual covered inputs.
- **Other code or behavior changes:** obtain independent assessment of the delta and its interaction with previously reviewed inputs. Do not hide new features, unrelated edits or substantive conflict resolutions inside a repair exemption. Use the affected predeclared unit's remaining review budget; at its limit, reconcile with the maintainer before dispatching more work.
- **Comments, test names, documentation or commit-message changes only:** the coordinator may carry review forward after checking that behavior and relevant build inputs are unchanged. A compiler directive inside a comment, an executable documentation change or an altered test assertion does not qualify merely because of its file or label.
- **Rebase to an identical tree:** retain the original reviewed version and record the tree equivalence. Reassess evidence that also depends on commit metadata or the comparison base.

Record the old/new versions, the inspected delta and the reason for carry-forward, policy-permitted verification without recheck, or renewed review. Preserve each finding's disposition. Independent review may cover a delta rather than repeat the entire branch, but its conclusion must identify the resulting candidate it covers. Report unreviewed repair deltas explicitly; satisfying a repair policy does not turn them into independently reviewed code.

## Multiple PRs or merge requests

Establish dependencies, candidate heads and intended merge order. Test each candidate against the base that will actually precede it, using the project's existing integration method, a task-owned scratch worktree or merge simulation. Checking every PR against the original main alone does not establish that later positions still merge or work together.

`git merge-tree --write-tree <base-commit> <candidate-commit>` is one conflict check. To simulate a sequence before merging, use temporary integration commits or a scratch worktree; a returned tree ID alone is not the next base commit. Conflict freedom does not prove behavioral compatibility, so review and verify affected combinations too.

After each actual merge, promptly update dependent candidates and recheck remaining order. Record any local conflict resolution that is not yet pushed. Code changes made while resolving conflicts need independent delta review and affected checks before the resulting head is eligible to merge.

For a delivery spanning independent repositories, also read [multi-repository delivery](multi-repo.md). Reconcile the linked candidate set, including verification-only units and external configuration or deployment inputs. Run `task_card.py check` once per independent Git repository; its report covers linked worktrees of that repository only. Per-repository success does not replace required combination checks, environment acceptance, external-owner evidence or ordered rollback validation.

## Endpoint readiness

Name the actual completion endpoint: a local result, reviewable PR/MR, merge, versioned artifact, release or deployment stage. Apply the relevant checks and authority to that endpoint; publication readiness does not establish that publication or rollout occurred. For artifacts or deployments, pin the actual artifact/configuration/environment and verify any required promotion order, health or rollback conditions. Use the project's available tools and evidence; this workflow does not add a release or deployment backend.

Use this evidence at the authorized endpoint:

| Requirement | Evidence needed |
|---|---|
| Authority | Current applicable user/project grant, including conditions and expiry |
| Candidate | Actual candidate identity and relevant inputs; full head/working-tree state for Git, artifact/configuration/environment versions when applicable |
| Review | Initial independent review, actual reviewed version, later delta, and completion of the project's repair recheck policy or allowed carry-forward |
| Findings | Every confirmed blocker resolved; major/minor findings disposed of under project policy; required evidence and decisions satisfied |
| Checks | All required gates passed on applicable inputs, including manually triggered/platform checks outside aggregate CI |
| Acceptance | Actual scenario coverage and limits, or an explicit authorized waiver/deferment where the task permits it |
| Decisions | No decision blocking the selected endpoint or requested hold remains |

Read fresh remote head/check state before a merge. Pin the assessed head through the platform's exact-head guard when available, such as GitHub's `--match-head-commit`. For artifact promotion or deployment, use an immutable artifact/version guard where available. If relevant inputs moved, reconcile the delta before proceeding. A missing or failed requirement leaves endpoint readiness pending with an owner; creating a PR or finishing a waiting observer does not satisfy that requirement.

An accepted limitation and a passed check are different claims. A permitted waiver of an unexecuted check does not accept a confirmed blocker. Keep an explicit waiver or narrower endpoint tied to its authorization; never relabel an unexecuted check as passed or claim the same delivery complete with an unresolved blocker. Review-budget exhaustion is an escalation, not completion. Stop at the authorized endpoint, retaining requirements for any later stage without implying authority to perform it.

## Resources and final records

Preserve evidence needed to support the results, then reconcile owned processes, host tasks, observers, inbox results and temporary execution directories. Check ownership before removing anything. A stopped observer can leave a host terminal behind; a disappeared terminal cannot prove CI passed.

For Git-backed inputs, run `task_card.py check --task-dir <task-dir> --repo <repo>` for a read-only debt report, separately for each independent repository in a multi-repository candidate set. Do not pass a non-Git artifact directory as a repository: inspect its records, retained inputs, inbox state and owned resources directly. An invalid repository or failed Git inspection is an error. An unreadable linked checkout has `dirty: null` plus an `error`; its state is unknown and needs reconciliation before a clean-resource claim. Inspect `prunable` entries rather than treating them as safe to delete automatically.

The report lists debts rather than enforcing all delivery gates. Its exit code alone does not approve the task; inspect the card, pending results, changed artifacts, checkout state and actual host resources. Update authorized external descriptions to match the final candidate, or prepare the exact correction when external writing is outside scope. Keep historical evidence versioned. Close registered inboxes and set the current task card to `Status: closed` last.
