# <Task> — independent review round <n>

- Delivery ID: `<task>.review.r<n>`
- From: coordinator. To: independent reviewer with fresh context. An agent handoff within the existing authorized task.

## Inputs

- Candidate: `<code/artifact identity and relevant local/config/data/build inputs>` at `<accessible location>`, compared with `<actual base; use full SHAs for Git>`.
- Goal and settled decisions: `<links>`.
- Rules: `<applicable repository instructions, review/design guidance>`.
- Prior round and claimed fixes, if any: `<artifacts and delta>`.
- Combination risks: `<other affected branches/state, or none>`.
- Review method: `<absolute skill path>/references/review-method.md`, with the linked project guidance.
- Severity and treatment: `<absolute skill path>/references/review-policy.md`; `<project-added blocker conditions, major/minor treatment and repair recheck policy>`.
- Review unit and round: `<predeclared unit ID/scope, current round/finite total; interaction coverage, prior results and selected repair IDs; material planned implementation still outside this candidate, if any>`.

Inspect the candidate independently. The implementer's report is a claim to check. In the initial review, cover the whole assigned change: closely read handwritten code/text, check generated sources and output consistency/semantics, and use suitable comparisons or integrity checks for non-text artifacts. State methods, sampling limits and unavailable scope. Follow affected paths from input/trigger to observable result using the stages the delivery has. Later rounds focus on selected fixes, delta and interactions; report real new defects but do not reopen resolved/accepted findings without new evidence. Flag a settled decision when concrete evidence shows it cannot hold.

## Boundaries

Product code is read-only. Write only `<result path and allowed scratch/evidence locations>`. Coordinate tests sharing mutable caches with `<verification owner / actual isolation or lock>`. Stop owned background commands before handing back.

Review stable, identified inputs. If the candidate changes while you inspect it, state exactly which version your conclusion covers and what delta remains. Fix rechecks follow the supplied project policy; a verified repair may require no further independent review. Do not claim independent coverage for that delta. Apply the skill's closeout rules to other changes and carry-forward cases.

A proposed blocker needs an applicable requirement/source, reachable trigger, evidence, disqualifying consequence and resolution criterion. Missing evidence is not proof of a blocker defect. Major/minor findings and recommendations are not automatic repair orders; the coordinator reconciles actual user impact, accepted scope and verification cost before selecting treatment. Report new defects without automatically prescribing another repair/review task. Do not demand another round just to eliminate suggestions. At the unit's budget limit, report remaining requirements and non-convergence instead of initiating another cycle. Renaming or splitting reviewed work does not replenish its budget.

Reuse applicable test evidence and recoverable candidate sources instead of repeating full gates or source copies. Read the complete assigned change with appropriate methods; use existing coverage notes and targeted follow-up reads to avoid repeatedly dumping unchanged rules, full history or already available file ranges. Genuine recovery still requires applicable rules and inputs. Return concise evidence summaries with full logs on disk. Classify failures before rerunning and preserve unresolved uncertainty. Read actual full SHAs for Git-backed inputs and actual artifact/configuration versions where relevant; retain your findings as immutable artifacts. A notification or an implementer's completion claim is not review evidence.

## Result and return

Write `<task-dir>/review/<delivery-id>.md`: verdict on the actual version, round and covered scope; findings added/resolved/remaining with stable ID, proposed blocker/major/minor severity, requirement/source, file:line, trigger, evidence (mark inference), consequence and resolution criterion. Check affected comments and test names for stale claims. Distinguish confirmed defects, recommendations and missing evidence; state what remains under the project's policy rather than treating every suggestion as blocking.

Return through the assignment's selected path; keep the artifact immutable:

```text
Result: <delivery-id>
Artifact: <absolute result path>
SHA-256: <artifact digest>
Version: <reviewed candidate identity and relevant inputs; full sha for Git>
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
