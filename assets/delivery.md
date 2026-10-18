# Project delivery conventions

<!-- After setup confirmation, copy into the target project's .delivery/delivery.md, fill from actual project sources,
     and remove irrelevant fields. This Markdown is read by the agent, not parsed by scripts.
     Paths are relative to this file; ../AGENTS.md points to the repository root.
     Resolve applicable choices as inherited, default adopted or project-specific, with a source.
     Inapplicability needs a reason. Pending items need an affected action and next owner;
     they do not count as completed policy setup. Task results belong in runs/<task>/task.md. -->

## Project context

- Repository instructions: `<path, for example ../AGENTS.md>`.
- Planning/decision index: `<path or existing source>`.
- Architecture/design principles: `<path or existing source>`.
- Review and delivery guidance: `<paths; link existing rules rather than duplicate them>`.
- Delivery project instructions: `<actual loaded project instruction source and setup guide>`.
- Local setup receipt: `setup.md` under the default layout; machine paths and host verification belong there, while actual connection IDs remain task-local.

## Environment and isolation

- Setup and runtime prerequisites: `<documented setup command or link>`.
- Supported environments: `<platforms/runtimes relevant to this project>`.
- Acceptance isolation: `<fixture, test home/profile, service ports and data boundaries, or SOP link>`.
- Shared resources: `<cache, database, device or machine lock; when serialization is needed>`.

## Verification

| Check | Actual command or workflow | When required | Coverage and prerequisites |
|---|---|---|---|
| Iteration checks | `<commands>` | `<affected code/behavior>` | `<what these establish>` |
| Stable-candidate gate | `<command>` | `<applicability>` | `<included checks>` |
| Commit hooks | `<actual hook commands or none configured>` | `<trigger>` | `<what already runs; source path>` |
| Remote CI | `<workflow/check names>` | `<trigger>` | `<required checks and platform coverage>` |
| Conditional lanes | `<one row per relevant lane>` | `<concrete change trigger>` | `<extra environment/manual launch needed>` |

- Evidence reuse: `<project-specific conditions beyond the skill's version/input rules, if any>`.
- Suspected flakes: `<bounded retry policy and case-log location, or no project-specific policy>`.
- Hook exemptions: `<existing authorization source, covered hooks/actions, conditions, replacement checks and validity; or none established>`.

## Review and acceptance

The defaults below are a proposal to reconcile with existing project rules during setup. Record each resolved value and source; an installed template is not evidence that choices were confirmed. General severity and convergence rules live in the installed skill's `references/review-policy.md`.

| Policy | Proposed general default | Resolved value and source/status |
|---|---|---|
| Initial review and method | Independent initial review for substantial complete delivery; the skill's review method plus project guidance | `<value; inherited/default adopted/project-specific>` |
| Additional blocker conditions | None beyond the skill's baseline; every confirmed blocker must be resolved | `<extra conditions and source, or explicitly none>` |
| Major treatment | Coordinator selects worthwhile in-scope repairs; otherwise accept/defer with rationale | `<required/optional repairs and decision owner>` |
| Minor treatment | No automatic repair; record a disposition and select only worthwhile in-scope fixes | `<required/optional repairs and decision owner>` |
| Blocker repair recheck | Targeted independent review/retest after verification | `<independent recheck or writer verification only>` |
| Major/minor repair recheck | Writer verification; no automatic independent review | `<policy for each severity>` |
| Review units and budget | Three rounds per predeclared unit: initial full review and at most two incremental rechecks; retain across sessions | `<unit boundary convention, finite total and extension decision owner; actual units/counts belong in task records>` |
| Separate text audit | When project rules or the change warrant one; changed/invalidated text is always inspected | `<every PR/MR, release or conditional trigger; independent auditor, scope and execution point>` |
| Change presentation | Concise comparison/demonstration suited to the changed behavior and its audience | `<trigger, UI/CLI/API/artifact/plan evidence, location, or reason inapplicable; new capabilities need no invented before state>` |

- Behavior/platform acceptance: `<changes requiring real-host/manual evidence; existing SOPs>`.
- Completion criteria: `<project-specific gates; the current task defines its actual endpoint>`.
- Pending policy/check facts: `<item, affected action, next owner, or none>`.
- Policy resolution: `<complete/pending; decision source; integration/loading status remains in setup.md>`.

## Records

- Task root: `runs/` unless the project uses another established location.
- Per-task entry: `runs/<task>/task.md` under this convention.
- Evidence and diagnostics: `<tool output locations; retain links instead of duplicating evidence>`.
- Visibility/version control: `.delivery/` is local and private by default, using Git's local exclusion without editing the target project's `.gitignore`; link existing alternative record conventions when retained. Exclusion does not make existing tracked files private.

## Publication and authorization

- Delivery endpoint: `<local result, reviewable PR/MR, merge, versioned artifact, release or deployment stage; task records name the selected endpoint>`.
- Branch/commit/PR/MR conventions: `<existing guidance when applicable>`.
- Merge conditions and method: `<required initial review and repair recheck policy, resolved blockers, checks/platform evidence, actual PR dependencies/order and allowed method>`.
- Existing project grants: `<source, authorized actions, scope, conditions and expiry; or none established; identify standing merge/publication grants separately from per-task grants>`.
- Release/deployment rules: `<existing guidance when applicable>`.

Only actual applicable user or project authorization permits publication, merge, release or deployment. Task-specific grants are recorded with their source in the task record.
