# <Task> — independent review round <n>

- Delivery ID: `<task>.review.r<n>`
- From: coordinator. To: independent reviewer with fresh context. An agent handoff within the existing authorized task.

## Inputs

- Candidate: `<branch>` at `<full sha>` in `<worktree>`, compared with `<base sha>`.
- Goal and settled decisions: `<links>`.
- Rules: `<applicable repository instructions, review/design guidance>`.
- Prior round and claimed fixes, if any: `<artifacts and delta>`.
- Combination risks: `<other affected branches/state, or none>`.
- Review method: `<absolute skill path>/references/review-method.md`, with the linked project guidance.
- Severity and treatment: `<absolute skill path>/references/review-policy.md`; `<project-added blocker conditions, major/minor treatment and repair recheck policy>`.
- Round: `<current round/finite total for this scope; prior results and selected repair IDs>`.

Inspect the code independently. The implementer's report is a claim to check. In the initial review, read the full assigned diff and necessary affected paths. Later rounds focus on the selected fixes, delta and interactions; report real new defects but do not reopen resolved/accepted findings without new evidence. Flag a settled decision when concrete evidence shows it cannot hold.

## Boundaries

Product code is read-only. Write only `<result path and allowed scratch/evidence locations>`. Coordinate tests sharing mutable caches with `<verification owner / actual isolation or lock>`. Stop owned background commands before handing back.

Review stable, identified inputs. If the candidate changes while you inspect it, state exactly which version your conclusion covers and what delta remains. Fix rechecks follow the supplied project policy; a verified repair may require no further independent review. Do not claim independent coverage for that delta. Apply the skill's closeout rules to other changes and carry-forward cases.

A proposed blocker needs an applicable requirement/source, reachable trigger, evidence, disqualifying consequence and resolution criterion. Missing evidence is not proof of a blocker defect. Major/minor findings and recommendations are not automatic repair orders; the coordinator confirms treatment. Do not demand another round just to eliminate suggestions. At the budget limit, report remaining requirements and non-convergence instead of initiating another cycle.

Reuse applicable test evidence instead of repeating a full gate on unchanged inputs. Classify failures before rerunning and preserve unresolved uncertainty. Read actual full SHAs from Git; retain your findings as immutable artifacts. A notification or an implementer's completion claim is not review evidence.

## Result and return

Write `<task-dir>/review/<delivery-id>.md`: verdict on the actual version, round and covered scope; findings added/resolved/remaining with stable ID, proposed blocker/major/minor severity, requirement/source, file:line, trigger, evidence (mark inference), consequence and resolution criterion. Check affected comments and test names for stale claims. Distinguish confirmed defects, recommendations and missing evidence; state what remains under the project's policy rather than treating every suggestion as blocking.

Return through the assignment's selected path; keep the artifact immutable:

```text
Result: <delivery-id>
Artifact: <absolute result path>
SHA-256: <artifact digest>
Version: <reviewed full sha and any local inputs>
Verdict: <one line with blocker count>
Decisions needed: <none, or specific decisions>
```

For an inbox return, publish before ending the round:

```text
python3 <skill>/scripts/queue_result.py --task <task-id>
  --delivery-id <delivery-id> --sender reviewer --artifact <absolute result>
  --version <reviewed-version> --summary <verdict>
  --outbox <task-dir>/outbox-reviewer --mailbox <registered-inbox>
  [--thread <registered-native-uuid, codex-queue only>]
```
