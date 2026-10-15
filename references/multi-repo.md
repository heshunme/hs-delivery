# Multi-repository delivery

Read this when one accepted task spans multiple independent Git repositories. A linked
worktree whose Git common directory belongs to the same repository is not a separate
repository for these rules.

## Resolve authority before assigning work

Create a short authority map when plans, TODOs, audits and historical designs coexist.
Apply current user instructions first, followed by the accepted current execution plan,
the maintained design sources it names, then supporting TODO or audit material. Dates and
filenames alone do not establish precedence.

Record concrete conflicts and which later decision supersedes each one. Assignments link
the authoritative plan and repeat only superseded items that could otherwise cause a
participant to do withdrawn work. Historical findings remain evidence about their
observed version; recheck them against the current candidate before treating them as open.

## Choose one coordination repository

Keep one task record in an actual Git repository or established project record location
that all participants can access. Do not initialize records independently in every member
repository, and do not treat a non-Git aggregate directory as a repository.

Classify each delivery unit:

- **write candidate:** product changes are authorized in its identified checkout;
- **verification-only:** inspect or test it, but do not change product code;
- **external dependency:** another owner supplies configuration, deployment or evidence;
- **out of scope:** retained only to prevent accidental expansion.

Moving a unit into the write set is a scope change. Obtain any required decision or
authorization before assigning a writer.

## Pin the candidate set

For a multi-repository task, the task card may use:

```text
Candidate: candidate set at <absolute-path>
```

Keep the linked candidate set small. For each unit record its repository or external
identity, base, current full version plus relevant local inputs, role, owner, stage,
review coverage and verification state. Git commits identify code; external bundle,
configuration and deployment versions remain distinct inputs rather than pretend Git
candidates.

Each review and test result names the exact unit versions and combination it covers.
Changing one unit does not invalidate unrelated evidence automatically, but combination
evidence must be reassessed when any relevant member changes.

## Assign and verify by boundary

Use one writer per checkout. Give each participant the applicable repository instructions,
the shared accepted plan, its unit's write boundary, and the other pinned versions that
affect its contract. Independent repository checks do not establish cross-repository
behavior.

Separate:

1. per-repository build, test and review;
2. cross-version contract or integration checks;
3. environment or platform acceptance;
4. external-owner evidence and decisions;
5. publication, rollout and rollback authorization.

Run expensive combination checks only after the relevant candidates are stable. Preserve
old-producer/new-consumer and ordered rollout combinations when the accepted plan requires
them. An unavailable environment stays unexecuted with an owner; another environment does
not silently substitute for it.

## Reconcile the set

At closeout, run the normal task-card audit separately for every independent Git
repository in scope. Then reconcile the candidate set, cross-repository findings,
combination checks, external dependencies, intended publication order and rollback order.
No single repository's clean audit or passing test suite closes the whole task.
