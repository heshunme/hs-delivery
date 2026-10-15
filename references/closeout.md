# Review coverage and delivery closeout

Read this when a reviewed candidate changes, when preparing publication/merge or when closing a delivery task. Project-specific gates and permissions still come from the actual task and project rules.

## Review coverage

Record the independent review's actual full SHA and relevant local inputs. Compare them with the current candidate and inspect the full delta, including changed dependencies, generated files and executable tests.

- **Code or behavior changes:** obtain an independent review of the delta and its interaction with the previously reviewed code. A coordinator's assessment or a passing retest alone does not extend independent code-review coverage.
- **Comments, test names, documentation or commit-message changes only:** the coordinator may carry review forward after checking that behavior and relevant build inputs are unchanged. A compiler directive inside a comment, an executable documentation change or an altered test assertion does not qualify merely because of its file or label.
- **Rebase to an identical tree:** retain the original reviewed version and record the tree equivalence. Reassess evidence that also depends on commit metadata or the comparison base.

Record the old/new versions, the inspected delta and the reason for carry-forward or renewed review. Preserve each finding's disposition and return affected fixes for independent review/retest. Review may cover a delta rather than repeat the entire branch, but its conclusion must identify the resulting candidate it covers.

## Multiple PRs

Establish dependencies, candidate heads and intended merge order. Test each candidate against the base that will actually precede it, using the project's existing integration method, a task-owned scratch worktree or merge simulation. Checking every PR against the original main alone does not establish that later positions still merge or work together.

`git merge-tree --write-tree <base-commit> <candidate-commit>` is one conflict check. To simulate a sequence before merging, use temporary integration commits or a scratch worktree; a returned tree ID alone is not the next base commit. Conflict freedom does not prove behavioral compatibility, so review and verify affected combinations too.

After each actual merge, promptly update dependent candidates and recheck remaining order. Record any local conflict resolution that is not yet pushed. Code changes made while resolving conflicts need independent delta review and affected checks before the resulting head is eligible to merge.

## Publication and merge readiness

Use this evidence at the authorized endpoint:

| Requirement | Evidence needed |
|---|---|
| Authority | Current applicable user/project grant, including conditions and expiry |
| Candidate | Current full head and relevant working-tree state |
| Review | Independent code review covering that head, with any allowed carry-forward rationale |
| Findings | Each finding fixed/verified, accepted with rationale or deferred to a reachable follow-up; unresolved requirements visible |
| Checks | All required gates passed on applicable inputs, including manually triggered/platform checks outside aggregate CI |
| Acceptance | Actual scenario coverage and limits, or an explicit authorized waiver/deferment where the task permits it |
| Decisions | No merge-blocking maintainer decision or requested hold remains |

Read fresh remote head/check state before a merge. Pin the assessed head through the platform's exact-head guard when available, such as GitHub's `--match-head-commit`. If the head moved, reconcile its delta before proceeding. A missing or failed requirement leaves merge readiness pending with an owner; creating a PR or finishing a waiting observer does not satisfy that requirement.

An accepted limitation and a passed check are different claims. Keep an explicit waiver or narrower endpoint tied to its authorization; never relabel an unexecuted check as passed. Stop at local completion or a reviewable PR when that is the authorized endpoint.

## Resources and final records

Preserve evidence needed to support the results, then reconcile owned processes, host tasks, observers, inbox results and temporary execution directories. Check ownership before removing anything. A stopped observer can leave a host terminal behind; a disappeared terminal cannot prove CI passed.

Run `task_card.py check --task-dir <task-dir> --repo <repo>` for a read-only debt report. An invalid repository or failed Git inspection is an error. An unreadable linked checkout has `dirty: null` plus an `error`; its state is unknown and needs reconciliation before a clean-resource claim. Inspect `prunable` entries rather than treating them as safe to delete automatically.

The report lists debts rather than enforcing all delivery gates. Its exit code alone does not approve the task; inspect the card, pending results, changed artifacts, checkout state and actual host resources. Update authorized external descriptions to match the final candidate, or prepare the exact correction when external writing is outside scope. Keep historical evidence versioned. Close registered inboxes and set the current task card to `Status: closed` last.
