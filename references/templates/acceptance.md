# <Task> — acceptance round <n>

- Delivery ID: `<task>.acceptance.r<n>`
- From: coordinator. To: acceptance owner. An agent handoff within the existing authorized task.

## Candidate and environment

- Candidate: `<source/artifact identity, relevant config/data/dependencies and local changes; full sha for Git>`, prepared with `<method>`.
- Environment: `<conditions relevant to the scenarios; platform, device, route or isolation as applicable>`.
- Existing scripts and SOPs: `<paths>`.
- Write/data boundaries: `<fixtures and evidence allowed; resources to preserve>`.
- Shared bottlenecks and execution coordination: `<owner, isolation or actual lock>`.
- Finding policy: `<absolute skill path>/references/review-policy.md`; `<project additions, selected repair IDs and required rechecks>`.

## Scenarios

<Meaningful scenarios, each with fixture identity/state, actions, observable result, pass condition and existing evidence. Include the host/platform combination the changed chain actually needs.>

Choose automation based on expected repetition, error risk, existing tooling and setup/maintenance cost. Technical scriptability alone does not require a new script; a one-off manual check may be sufficient with explicit steps, observations and limits. When automation is worthwhile, batch actions, condition-based waits with hang deadlines and assertions into a bounded command, then inspect its result instead of driving each action and sleep in separate model turns. Use human observation for claims automation does not establish.

Follow the project's change-presentation policy with evidence suited to its audience: UI views/interactions, CLI output, API examples, artifact comparisons or an infrastructure plan. Compare before/after when a meaningful baseline exists; demonstrate a new capability without inventing one. Presentation evidence supports its specific claims and does not replace required checks.

For measurements, retain sample count, method/boundaries and the inputs/environment that affect the quantity measured. Select relevant conditions: route for network measurements, build/dependency graph for build or startup costs, window visibility/focus for affected UI timing, or realistic data shape for data workloads. Repeated-character data is not representative of compression or transfer workloads unless that is the intended workload. Record and serialize shared bottlenecks when present; separate queue time from execution time when interpreting results. Do not require irrelevant environment fields merely to fill a checklist.

Keep tested inputs stable and identify the actual candidate and its relevant inputs, including full SHA/local changes for Git-backed code. An unchanged SHA is insufficient when a relevant configuration, dataset, dependency or artifact changed. Reuse applicable earlier evidence with its original version and rationale. Classify failures before rerunning; a passing rerun does not explain the first failure. Respect shared-cache/resource ownership even when no product files are edited. Report unexecuted scenarios and unsupported environments explicitly rather than counting them as passed.

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
