# <Task> — acceptance round <n>

- Delivery ID: `<task>.acceptance.r<n>`
- From: coordinator. To: acceptance owner. An agent handoff within the existing authorized task.

## Candidate and environment

- Candidate: `<actual full sha and local inputs>`, built with `<method>`.
- Environment: `<platform, devices, route, isolated profile/home/ports>`.
- Existing scripts and SOPs: `<paths>`.
- Write/data boundaries: `<fixtures and evidence allowed; resources to preserve>`.
- Shared bottlenecks and execution coordination: `<owner, isolation or actual lock>`.
- Finding policy: `<absolute skill path>/references/review-policy.md`; `<project additions, selected repair IDs and required rechecks>`.

## Scenarios

<Meaningful scenarios, each with fixture identity/state, actions, observable result, pass condition and existing evidence. Include the host/platform combination the changed chain actually needs.>

For repeatable scenarios that can be scripted, run the actions, condition-based waits with hang deadlines and assertions in one command, then inspect its result. Do not drive those scenarios one click, sleep and screenshot per model turn. Use manual observation when the scenario requires it and explain what the script cannot establish. Screenshots support visual claims, including before/after previews required by project policy.

For measurements, retain sample count and each sample's relevant conditions: actual host/route, build and module graph, realistic fixture/data shape, shared bottlenecks, and timing boundaries. Record window visibility/focus when it affects UI timing. Repeated-character data is not representative evidence for compression or transfer performance unless that is the intended workload. Serialize runs sharing a bottleneck and separate queue time from execution time when interpreting results.

Keep the tested inputs stable and identify the actual full SHA plus local changes. Reuse applicable earlier evidence with its original version and rationale. Classify failures before rerunning; a passing rerun does not explain the first failure. Respect shared-cache/resource ownership even when no product files are edited. Report unexecuted scenarios and unsupported environments explicitly rather than counting them as passed.

## Result and return

Write `<task-dir>/acceptance/<delivery-id>.md`: per-scenario method, observed version/environment, samples, results and limits; findings with proposed severity, trigger, requirement/source, evidence, impact and resolution criterion; unexecuted requirements; final environment state. Distinguish a confirmed blocker from missing acceptance evidence. Return findings for coordinator disposition instead of starting repairs or another review cycle. A verification-only fix does not need another independent review unless project policy requires it. Keep raw evidence at `<evidence-dir>` and reproduction scripts at `<script-dir>`. Remove secrets from shared artifacts.

Stop owned processes and restore `<required final environment state>`. Any explicitly authorized continuing work needs its binding, pending status and accepting owner in the result. Keep the published artifact immutable; corrections use a new result file and delivery ID.

```text
Result: <delivery-id>
Artifact: <absolute result path>
SHA-256: <artifact digest>
Version: <tested-version>
Verdict: <one line>
Decisions needed: <none, or specific decisions>
```

For an inbox return, publish before ending the round:

```text
python3 <skill>/scripts/queue_result.py --task <task-id>
  --delivery-id <delivery-id> --sender acceptance --artifact <absolute result>
  --version <tested-version> --summary <one-line-result>
  --outbox <task-dir>/acceptance/outbox --mailbox <registered-inbox>
  [--thread <registered-native-uuid, codex-queue only>]
```
