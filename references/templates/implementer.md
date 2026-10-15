# <Task> — implementation round <n>

- Delivery ID: `<task>.implementation.r<n>`
- From: coordinator. To: sole writer of `<worktree>`. An agent handoff within the existing authorized task.

## Scope and inputs

<Goal, accepted design/decisions, scope items, exclusions and completion endpoint. Link the source artifacts. Flag a material conflict with accepted behavior before the dependent step; make and record routine implementation choices.>

- Base: `<branch>` at `<full sha>`.
- Worktree: `<actual path and creation mechanism, if needed>`.
- Skill: `<absolute skill directory>`. Task record: `<absolute task.md>`.
- Write boundary: `<code checkout and result/evidence locations>`.
- Project rules: `<applicable instructions and delivery/check guidance>`.
- Shared state or combination risks: `<other work, mutable caches, resource owner, or none>`.

## Checks and authority

<Actual iteration checks, stable-candidate gates and conditional lanes from the project's rules. Account for hooks and earlier unchanged-input evidence; see the skill's verification reference. Name any shared lock and owner.>

<Allowed commit/publication actions and applicable grant sources. Follow required hooks and repository commit conventions.>

## Checkpoint

<Publish and stop before a feedback-dependent next step, or hand back when this round's scope is complete.>

Before ending, stop or explicitly hand over owned background writers; give the actual HEAD and working-tree state.

## Result and return

Write `<task-dir>/results/<delivery-id>.md`: actual full SHA and local inputs, outcome per scope item, deviations/reasons, shared code touched, meaningful tests/checks and their tested inputs/outcomes, unresolved requirements and next owner. Keep it immutable after publication.

<Keep the return path chosen by the coordinator; see the assignment guidance.>

```text
Result: <delivery-id>
Artifact: <absolute result path>
SHA-256: <artifact digest>
Version: <actual full sha and any local inputs>
Verdict: <one line>
Decisions needed: <none, or specific decisions>
```

For an inbox return, publish before ending the round:

```text
python3 <skill>/scripts/queue_result.py --task <task-id>
  --delivery-id <delivery-id> --sender implementer --artifact <absolute result>
  --version <actual-version> --summary <one-line-result>
  --outbox <task-dir>/outbox-implementer --mailbox <registered-inbox>
  [--thread <registered-native-uuid, codex-queue only>]
```
