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
