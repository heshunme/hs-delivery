# <Task> — acceptance round <n>

- Delivery ID: `<task>.acceptance.r<n>`
- From: coordinator. To: acceptance owner. An agent handoff within the existing authorized task.

## Candidate and environment

- Candidate: `<actual full sha and local inputs>`, built with `<method>`.
- Environment: `<platform, devices, route, isolated profile/home/ports>`.
- Existing scripts and SOPs: `<paths>`.
- Write/data boundaries: `<fixtures and evidence allowed; resources to preserve>`.
- Shared bottlenecks and execution coordination: `<owner, isolation or actual lock>`.

## Scenarios

<Meaningful scenarios, each with fixture identity/state, actions, observable result, pass condition and existing evidence. Include the host/platform combination the changed chain actually needs.>

Automate repeatable steps and assertions with condition-based waits and bounded hang detection where useful. For measurements, record sample count, timing boundaries and environmental factors affecting interpretation. Screenshots support claims that need visual evidence.

## Result and return

Write `<task-dir>/acceptance/<delivery-id>.md`: per-scenario method, observed version/environment, samples, results and limits; findings with impact and evidence; unexecuted requirements; final environment state. Keep raw evidence at `<evidence-dir>` and required reproduction scripts at `<script-dir>`. Remove secrets from shared artifacts.

Stop or explicitly hand over owned processes and restore `<required final environment state>`. Keep the published artifact immutable.

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
