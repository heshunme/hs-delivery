# <Task> — acceptance round <n>

- Delivery ID: `<task>.acceptance.r<n>`
- From: coordinator. To: acceptance owner. An agent handoff within the existing authorized task.

## Candidate and environment

- Candidate: `<source/artifact identity, relevant config/data/dependencies and local changes; full sha for Git>`, prepared with `<method>`.
- Environment: `<conditions relevant to the scenarios; platform, device, route or isolation as applicable>`.
- Existing scripts and SOPs: `<paths>`. Permitted verification-side mechanical corrections: `<scope, or none; product changes remain with the assigned writer>`.
- Write/data boundaries: `<fixtures and evidence allowed; resources to preserve>`.
- Shared bottlenecks and execution coordination: `<owner, isolation or actual lock>`.
- Finding policy: `<absolute skill path>/references/review-policy.md`; `<project additions, selected repair IDs and required rechecks>`.

## Scenarios

<Scenarios tied to the current delivery decision: relevant fixture/state, actions, observable result, pass condition and existing evidence. Identify the source and applicable conditions of costly requirements; distinguish hard requirements/required gates from engineering starting values or diagnostic observations. Include the host/platform combinations the changed chain actually needs.>

Choose sufficient evidence and a bounded return point before expensive work. If preparation keeps generating follow-ups, the method cannot answer the question, or the next step substantially expands instrumentation, matrices, data or resource use, return what is established, what remains necessary and a recommended next action to the coordinator. Adjust methods within scope; do not silently lower hard requirements or invent new ones from driver conditions. Local tool failures only block dependent operations.

Choose automation based on expected repetition, error risk, existing tooling and setup/maintenance cost. Technical scriptability alone does not require a new script; a one-off manual check may be sufficient with explicit steps, observations and limits. When automation is worthwhile, batch actions, condition-based waits with hang deadlines and assertions into a bounded command, then inspect its result instead of driving each action and sleep in separate model turns. Use human observation for claims automation does not establish. Preflight unverified or changed prerequisites through the actual worker identity/configuration/entry point; keep full logs on disk and return outcomes, failures and relevant excerpts. For auxiliary tools, verify the actual operation and downstream consumption, not merely that the script or page exists.

Follow the project's change-presentation policy with evidence suited to its audience: UI views/interactions, CLI output, API examples, artifact comparisons or an infrastructure plan. Compare before/after when a meaningful baseline exists; demonstrate a new capability without inventing one. Presentation evidence supports its specific claims and does not replace required checks.

For measurements, retain sample count, method/boundaries and the inputs/environment that affect the quantity measured. Select relevant conditions: route for network measurements, build/dependency graph for build or startup costs, window visibility/focus for affected UI timing, or realistic data shape for data workloads. Repeated-character data is not representative of compression or transfer workloads unless that is the intended workload. Record and serialize shared bottlenecks when present; separate queue time from execution time when interpreting results. Do not require irrelevant environment fields merely to fill a checklist.

Keep tested inputs stable and identify the actual candidate and its relevant inputs, including full SHA/local changes for Git-backed code. An unchanged SHA is insufficient when a relevant configuration, dataset, dependency or artifact changed. Reuse applicable earlier evidence with its original version and rationale. Classify failures before rerunning and preserve decisive original traces before cleanup; a passing rerun does not explain the first failure. Permitted mechanical fixture/path/reporting corrections can be completed in this round with original failures retained. Do not change in-review product code, weaken assertions or expand scope to obtain a pass. Respect shared-cache/resource ownership even when no product files are edited. Report unexecuted scenarios and unsupported environments explicitly rather than counting them as passed.

## Result and return

Write `<task-dir>/acceptance/<delivery-id>.md`: per-scenario method, observed version/environment, samples, results and limits; findings with proposed severity, trigger, requirement/source, evidence, impact and resolution criterion; unexecuted requirements; final environment state. Distinguish a confirmed blocker from missing acceptance evidence. Independent candidate assessment or required repair rechecking consumes the affected review unit's budget; return to the coordinator before expanding acceptance into that work. An unexpected finding does not require an unbudgeted review cycle. Return findings for coordinator disposition instead of starting repairs or another review cycle. A verification-only fix does not need another independent review unless project policy requires it. Keep raw evidence at `<evidence-dir>` and reproduction scripts at `<script-dir>`. Remove secrets from shared artifacts.

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
