# <Task> — independent review round <n>

- Delivery ID: `<task>.review.r<n>`
- From: coordinator. To: independent reviewer with fresh context. An agent handoff within the existing authorized task.

## Inputs

- Candidate: `<branch>` at `<full sha>` in `<worktree>`, compared with `<base sha>`.
- Goal and settled decisions: `<links>`.
- Rules: `<applicable repository instructions, review/design guidance>`.
- Prior round and claimed fixes, if any: `<artifacts and delta>`.
- Combination risks: `<other affected branches/state, or none>`.

Inspect the code independently. The implementer's report is a claim to check. Flag a settled decision when concrete evidence shows it cannot hold.

## Boundaries

Product code is read-only. Write only `<result path and allowed scratch/evidence locations>`. Coordinate tests sharing mutable caches with `<verification owner / actual isolation or lock>`. Stop owned background commands before handing back.

Review stable, identified inputs. If the candidate changes while you inspect it, state exactly which version your conclusion covers and what delta remains. Changed code needs independent delta review before coverage can extend to the new head. Comments/test-name/docs-only changes or an identical-tree rebase may be carried forward by the coordinator only with a recorded impact assessment under the skill's closeout guidance.

Reuse applicable test evidence instead of repeating a full gate on unchanged inputs. Classify failures before rerunning and preserve unresolved uncertainty. Read actual full SHAs from Git; retain your findings as immutable artifacts. A notification or an implementer's completion claim is not review evidence.

## Result and return

Write `<task-dir>/review/<delivery-id>.md`: verdict on the actual version, then findings with stable ID, severity, file:line, triggering scenario, evidence (mark inference), consequence and suggested fix. Check affected comments and test names for stale claims. Distinguish blocking findings from recommendations and unverified concerns.

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
