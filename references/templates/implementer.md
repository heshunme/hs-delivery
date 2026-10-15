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

Keep these rules when filling project-specific checks:

- Use one code writer for this checkout. Run expensive checks on stable inputs through the assigned verification owner; coordinate shared caches/locks before a concurrent test run.
- Account for checks already run by hooks. Do not repeat a full gate on unchanged relevant inputs; retain the original tested SHA and explain evidence reuse. For later changes, run required and affected checks rather than every available suite.
- Classify a failure before rerunning: candidate defect, environment/tool failure or suspected flake. Preserve the failure and follow the project's bounded retry policy. A passing rerun alone does not establish a cause.
- Preserve required hooks. Use a bypass only under an applicable existing exemption and perform its required replacement checks.
- Read actual full SHAs from Git in this checkout. Identify staged, unstaged and relevant added inputs separately; a SHA with a dirty flag cannot reconstruct those inputs.
- Stop at the named feedback checkpoint. Return affected fixes for independent review/retest; your own inspection does not extend independent review coverage to changed code.

## Checkpoint

<Publish and stop before a feedback-dependent next step, or hand back when this round's scope is complete.>

Before ending, stop owned background writers and confirm nothing continues changing the handed-back inputs. If the assignment explicitly permits background work to continue, record its process/host binding, pending status and accepting next owner instead of claiming the round is fully complete. Give the actual HEAD and working-tree state.

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
