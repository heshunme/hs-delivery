# Project-specific delivery conventions

Read the target project's existing rules and accepted task first. A small `.delivery/delivery.md` may fill gaps for repeated use, but adoption does not require creating it. Link existing sources; keep a rule in one maintained place.

Recover these facts for the current task:

| Area | Information needed |
|---|---|
| Context | Planning index, accepted decisions, design principles, current task record |
| Checks | Cheap iteration checks, full gates, hook coverage, conditional lanes/platforms, relevant commands |
| Review | Review method, unit boundaries, additional blocker conditions, major/minor treatment, repair rechecks, finite round budget and any separate text audit |
| Environment | Isolation recipe, data/device limits, shared resource locks and test prerequisites |
| Records | Task root, evidence locations, private/public boundaries, existing finding or flaky-test log |
| Publication | Applicable PR/MR, artifact or rollout conventions, permitted delivery endpoint and authorization sources |
| Host setup | Loaded project instruction source, local setup receipt and supported completion/resumption path |

Use repository instructions and actual scripts to establish check coverage. Another project's hook behavior, platform matrix, retry allowance, commit style or permission grant does not carry over.

For a project without conventions, use the skill's general defaults rather than silently omitting behavior or treating empty fields as decisions for the user. Read existing rules and scripts first. Present material conflicts, unknown required facts or actual authorization gaps with recommendations; do not ask users to rediscover commands or reconfirm settled decisions. Keep only dependent actions pending.

## Resolve delivery behavior

Keep three layers distinct: the skill supplies a general method and defaults; project conventions supply concrete checks and policy choices; actual user/project grants authorize actions. A filled policy field does not create authority to publish or merge.

Use these fallbacks when no established project or user policy provides a different choice. During initialization, show the applicable defaults in the proposed policy set so the user can retain or change them as a group.

| Area | General default or required project fact |
|---|---|
| Review method and first review | Use the skill's [review method](review-method.md); substantial complete delivery includes independent initial review. Link additional project guidance. |
| Severity | Use the [blocker/major/minor baseline](review-policy.md); confirmed blockers must be resolved. List project-added blocker conditions or explicitly state none. |
| Major/minor treatment | No automatic repair; the coordinator selects worthwhile in-scope fixes or records acceptance/deferment with rationale. A project may require particular classes to be fixed. |
| Repair rechecks | Blocker fixes get targeted independent review/retest; selected major/minor fixes get writer verification. The project may choose writer verification only or independent recheck for either severity. Every implemented fix needs verification evidence. |
| Review units and budget | Three code-review rounds per predeclared unit: initial full review plus at most two incremental rechecks. The task records boundaries, interactions and counts; the project may choose another finite budget. Retain the escalation and completion rules. |
| Comment/documentation audit | Inspect changed and invalidated explanatory text. Resolve when a separate independent audit is required, such as every PR/MR, release or specified change class, and its scope and execution point. |
| Change presentation | For changes people must assess, retain a concise comparison or demonstration appropriate to the audience: UI views/interactions, CLI output, API examples or an infrastructure plan. The project chooses triggers, format and evidence location. For a new capability without a prior baseline, show its outcome without fabricating a before state. |
| Checks and acceptance | Derive actual commands, hook coverage, conditional platforms, host acceptance and isolation from project sources. Unknown commands or required environments remain gaps, not invented defaults. |
| Verification budget | Use [verification guidance](verification.md), including evidence reuse and bounded failure diagnosis. Record any project lock, retry rule or hook exemption; absent an exemption, preserve hooks. |
| Endpoint and authority | Name the requested endpoint and existing grants, or none established. No publication, merge, release or deployment authority comes from this template. |

Record applicable policy sources as inherited, default adopted or project-specific; one link can identify the adopted default set without copying its table. Record project differences and meaningful inapplicability. A genuinely pending choice names its affected action and next owner; an uncovered field with an applicable default is not pending merely because it is blank. Routine execution can use the fallbacks without persistent infrastructure; initialization makes their adoption explicit. Apply existing repository requirements rather than letting a missing local setting erase them.

## Preparing delivery.md

Use [the starter template](../assets/delivery.md) to draft a project's `.delivery/delivery.md`. It is human-readable Markdown, not a script configuration schema. Fill it from actual repository instructions, scripts and established decisions. Resolve applicable behavior using the table above; remove irrelevant scaffolding only after recording why it does not apply. Missing facts stay explicit with their impact and next owner instead of becoming invented commands or passing checks.

Keep stable project conventions here: context links, supported environments, check coverage and triggers, review/acceptance requirements, record locations and publication rules. Current candidate identities, review units and counts, participant IDs, pending findings, observer state and test results belong in task records. Machine-local skill/interpreter paths, setup changes and host-loading observations belong in `.delivery/setup.md` or an equivalent local receipt; recipient and observer bindings remain task-local. The project contract links these records without duplicating their current contents. The default `.delivery/` records remain local and private, excluded through Git's local exclude file; setup does not introduce shared or tracked delivery records.

Relative paths in `.delivery/delivery.md` are resolved from that file's directory. Use `../AGENTS.md` to refer to root instructions; paths shown as `<repo>/...` identify the repository root explicitly. Project grants may be linked with their scope and conditions; a template or blank authorization slot supplies no permission.

## Paths and installation

- `<skill>` is the directory containing this skill's `SKILL.md` and scripts.
- `<repo>` is the target repository; helper installation location does not identify it.
- `<task-dir>` is the project's actual task record directory.
- `.delivery/delivery.md` is the project convention entry point.
- `.delivery/setup.md` is the default local setup receipt; it is not helper configuration or a task selector.
- `.delivery/runs/<task>/` is the fallback task location, not a requirement to reorganize existing project records.

Use absolute paths in assignments that cross worktrees or sessions. Do not copy machine-specific inbox state or observer bindings as part of installing the skill elsewhere. Keep private records out of published output; describe the behavior there in self-contained terms.

For adoption or incomplete setup, follow [project initialization and recovery](setup-and-recovery.md): inspect first, preview concrete changes and resolve any authorization gap before applying them; carry forward existing approval. This includes local Git exclusion without changing `.gitignore`, needed Python capabilities and a short pointer in the host's project instructions. Reading this project contract or preserving a task card does not establish instruction loading. Keep configuration, observed entry loading and verified recovery separate, and the destination-host trial visibly pending until [its acceptance scenarios](host-acceptance.md) are exercised.
