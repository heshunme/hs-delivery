# Project-specific delivery conventions

Read the target project's existing rules and accepted task first. A small `.delivery/delivery.md` may fill gaps for repeated use, but adoption does not require creating it. Link existing sources; keep a rule in one maintained place.

Recover these facts for the current task:

| Area | Information needed |
|---|---|
| Context | Planning index, accepted decisions, design principles, current task record |
| Checks | Cheap iteration checks, full gates, hook coverage, conditional lanes/platforms, relevant commands |
| Review | Review guidance, required independence and any separate comment audit |
| Environment | Isolation recipe, data/device limits, shared resource locks and test prerequisites |
| Records | Task root, evidence locations, private/public boundaries, existing finding or flaky-test log |
| Publication | PR conventions, permitted delivery endpoint and applicable authorization sources |
| Host setup | Loaded project instruction source, local setup receipt and supported completion/resumption path |

Use repository instructions and actual scripts to establish check coverage. Another project's hook behavior, platform matrix, retry allowance, commit style or permission grant does not carry over.

For a project without conventions, make ordinary choices proportionate to the change and record the ones needed for continuity. Ask only about missing decisions that materially affect the authorized work. Keep an approval-dependent action pending while doing unblocked preparation.

## Preparing delivery.md

Use [the starter template](../assets/delivery.md) to draft a project's `.delivery/delivery.md`. It is human-readable Markdown, not a script configuration schema. Fill it from actual repository instructions, scripts and established decisions; remove irrelevant sections. Mark missing facts as unknown instead of inventing commands or treating an unconfigured check as passed.

Keep stable project conventions here: context links, supported environments, check coverage and triggers, review/acceptance requirements, record locations and publication rules. Current candidate SHAs, participant IDs, pending findings, observer state and test results belong in task records. Machine-local skill/interpreter paths, setup changes and host-loading observations belong in `.delivery/setup.md` or an equivalent local receipt; recipient and observer bindings remain task-local. A shared project contract links these records without duplicating their current contents.

Relative paths in `.delivery/delivery.md` are resolved from that file's directory. Use `../AGENTS.md` to refer to root instructions; paths shown as `<repo>/...` identify the repository root explicitly. Project grants may be linked with their scope and conditions; a template or blank authorization slot supplies no permission.

## Paths and installation

- `<skill>` is the directory containing this skill's `SKILL.md` and scripts.
- `<repo>` is the target repository; helper installation location does not identify it.
- `<task-dir>` is the project's actual task record directory.
- `.delivery/delivery.md` is the project convention entry point.
- `.delivery/setup.md` is the default local setup receipt; it is not helper configuration or a task selector.
- `.delivery/runs/<task>/` is the fallback task location, not a requirement to reorganize existing project records.

Use absolute paths in assignments that cross worktrees or sessions. Do not copy machine-specific inbox state or observer bindings as part of installing the skill elsewhere. Keep private records out of published output; describe the behavior there in self-contained terms.

For adoption or incomplete setup, follow [project initialization and recovery](setup-and-recovery.md): inspect first, preview the concrete changes and obtain setup confirmation before writing them. This includes local Git exclusion without changing `.gitignore`, needed Python capabilities and a short pointer in the host's project instructions. Reading this project contract or preserving a task card does not establish instruction loading. Keep configuration, observed entry loading and verified recovery separate, and the destination-host trial visibly pending until [its acceptance scenarios](host-acceptance.md) are exercised.
