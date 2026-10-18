# Finding severity, repair policy and review convergence

Read this before assigning review, selecting repairs or deciding whether another round is needed. The project may add blocker conditions and choose major/minor treatment, repair recheck requirements and a finite round budget. Repository and user requirements still govern. Use [project conventions](project-contract.md) to resolve those choices; an empty field does not erase the defaults below.

## Classify the consequence

Severity describes impact, not an instruction to edit. The reviewer proposes a classification; the coordinator checks the evidence and records the disposition before assigning repairs.

| Level | Definition |
|---|---|
| blocker | A demonstrated problem makes the accepted delivery unusable or untrustworthy, or violates a non-negotiable delivery condition. It must be resolved before completion. |
| major | A substantial functional or quality defect with bounded impact or reliable recovery that does not meet a blocker condition. The project decides whether to repair it in this delivery. |
| minor | A limited defect or local clarity/consistency issue with small impact that does not meet the higher levels. The project decides whether to repair it. |

A preference, optional enhancement or speculative concern is not automatically a defect. Record an unproven concern as awaiting evidence, not as a confirmed blocker. A missing required check can block delivery readiness without proving a blocker defect in the code.

## Confirm a blocker

All three conditions must hold:

1. **Applicable scope:** the affected behavior, environment or existing guarantee is part of the accepted delivery.
2. **Reachable trigger:** a reproduction or a complete reachable code path establishes the failure. A hypothetical future consumer or unsupported setup does not suffice.
3. **Disqualifying consequence:** at least one condition below applies, with its actual impact explained.

| Condition | Evidence required |
|---|---|
| Data integrity | Valid user data can be irrecoverably lost or corrupted, or silently written to the wrong object without reliable detection or recovery. |
| Security or authorization boundary | A reachable path exposes credentials/protected data, bypasses required access isolation, or performs a consequential unauthorized side effect. |
| Core behavior | An explicitly promised core operation cannot complete or violates essential semantics so that the principal delivery goal does not hold. |
| Basic operation and recovery | Installation, startup or upgrade fails in a supported environment, or hangs, crashes or uncontrolled resource growth make the core service unavailable under supported use. |
| Explicit hard requirement | The implementation demonstrably violates an accepted non-negotiable condition, such as protocol compatibility, preserved data or required platform support. Cite its actual source. |

Low frequency does not downgrade a reachable integrity or security failure. A workaround changes the assessment only when it is reliable, discoverable and compatible with the accepted usage; manual data repair or luck is not reliable recovery. A red test needs diagnosis: environment failure and an obsolete assertion are not automatically product blockers. Writing style and architecture preferences are not hard requirements merely because a reviewer calls them such.

Each proposed blocker names the requirement/source, trigger, evidence, consequence and resolution criterion. Resolve classification disputes from those facts. If reviewers prescribe opposing fixes or the same finding returns without progress, reconcile the underlying requirement before another implementation round; escalate an unresolved material decision rather than oscillating between fixes.

## Decide treatment before dispatch

Confirmed blockers must be resolved. They cannot be accepted or deferred as unresolved blockers while claiming the same delivery complete. Correct an unsupported classification with evidence; do not relabel a real blocker to meet a budget. Only an explicit scope decision changes the delivery requirements, and its effect must be recorded rather than silently rewriting the finding.

For major/minor findings, apply the project's treatment policy. The fallback is to record them without automatically repairing them: the coordinator may select a repair within accepted scope when its benefit justifies the change and verification cost, otherwise accept it with rationale or defer it to a reachable follow-up. Unverified concerns get a bounded investigation when needed for a delivery decision. Do not turn every recommendation into work or broaden the task with opportunistic refactors.

Every implemented fix needs evidence against its resolution criterion. That evidence and an independent recheck are separate requirements. The project chooses, by severity, whether a repair needs independent review/retest or writer verification only. The fallback is a targeted independent recheck for blocker repairs and writer verification for selected major/minor repairs. State the resolved policy in assignments. If the project chooses writer verification only for a blocker fix, a verified fix does not automatically trigger a review round.

A chosen repair must satisfy its applicable checks and recheck policy. If it is abandoned or reverted, retain the finding and reassess the resulting candidate. New feature work, unrelated executable changes or substantive conflict resolutions are not repairs covered by a relaxed repair policy; they need independent assessment of the delta before completion. See [closeout](closeout.md#review-coverage) for accurate version claims.

## Bound the review cycle

The default budget is **three code-review rounds: one full review and at most two incremental rechecks per declared review unit**. A project may set another finite budget. By default the accepted deliverable is one unit. Before the first dispatch, record each unit's scope, completion condition and budget in the task record; a unit may be a PR/MR, package, independently assessable change or deployment stage. Repository and participant boundaries do not automatically define units. For multiple units, identify who covers their interactions and which unit's budget covers that review; declare a separate integration unit only when it has a real distinct scope.

Count a coordinated review of one candidate for that unit as one round even when several reviewers contribute; callbacks, result corrections and multiple findings are not separate rounds. Record the round when dispatched and retain consumed rounds across repairs, reviewer replacement, compaction, sessions and rebases. Independent, predeclared units have their own counts; exhausting one does not consume another's budget or permit reassignment of the exhausted work to it. Renaming, retroactive splitting, moving findings or calling a review an audit cannot reset a budget. A material scope change requires reconciliation of coverage and consumed rounds; record the maintainer's decision before extending or repartitioning work already reviewed. A standalone text audit does not consume a code-review round, but does not start another code-review cycle either.

An independent assessment of candidate code or a fix's resolution consumes a round, including an independent retest used as the required repair recheck. Ordinary writer verification and scheduled acceptance are not review rounds. Bounded advice about requirements or design options without assessing a candidate is not a code-review round; it also does not authorize more repair/review dispatch after the budget is exhausted. Count by the actual work, not the participant's title.

The first round covers the whole assigned change. Later rounds check selected repairs, remaining findings, the delta and its interactions with previously reviewed code. Report real newly discovered defects, but do not reopen resolved or accepted findings without new evidence or changing requirements. Group related repairs into one useful candidate; a new report alone does not require another round.

After each round, the coordinator records findings added/resolved/remaining, dispositions, candidate, actual review coverage and the next action under the project's repair policy. Finish review when:

- every confirmed blocker is resolved;
- initial review and all project-required repair rechecks/checks are satisfied on applicable inputs;
- remaining findings have explicit permitted dispositions and no required evidence or decision is outstanding.

Do not seek a report with no suggestions. If review is complete, proceed to the remaining authorized acceptance or closeout work.

At the round limit, reconcile the returned findings and evidence before any further dispatch. If completion conditions hold, finish review. Otherwise stop automatically assigning repair/review rounds and report the remaining requirements, per-round progress, reason for non-convergence and a recommended next action. The maintainer may extend the budget or decide scope/design; record that decision before continuing dependent work. Budget exhaustion is neither a pass nor permission to leave a blocker unresolved. Keep the requirement and next owner visible while continuing unrelated, unblocked work.
