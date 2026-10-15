# Project delivery conventions

<!-- Copy into the target project's .delivery/delivery.md, fill from actual project sources,
     and remove irrelevant fields. This Markdown is read by the agent, not parsed by scripts.
     Paths are relative to this file; ../AGENTS.md points to the repository root.
     Unknown facts stay explicit. Task progress and results belong in runs/<task>/task.md. -->

## Project context

- Repository instructions: `<path, for example ../AGENTS.md>`.
- Planning/decision index: `<path or existing source>`.
- Architecture/design principles: `<path or existing source>`.
- Review and PR guidance: `<paths; link existing rules rather than duplicate them>`.

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
- Hook exemptions: `<existing policy source and replacement checks, or none established>`.

## Review and acceptance

- Independent review: `<project requirements and applicable review guide>`.
- Separate comment/documentation audit: `<whether required and its trigger>`.
- Behavior/platform acceptance: `<changes requiring real-host/manual evidence; existing SOPs>`.
- User-visible previews: `<when required and where to retain them>`.
- Completion criteria: `<project-specific gates; the current task defines its actual endpoint>`.

## Records

- Task root: `runs/` unless the project uses another established location.
- Per-task entry: `runs/<task>/task.md` under this convention.
- Evidence and diagnostics: `<tool output locations; retain links instead of duplicating evidence>`.
- Visibility/version control: `<what is shared, tracked or ignored; where private artifacts belong>`.

## Publication and authorization

- Branch/commit/PR conventions: `<existing guidance>`.
- Merge conditions and method: `<required checks/review/platform evidence and allowed method>`.
- Existing project grants: `<source, authorized actions, scope, conditions and expiry; or none established>`.
- Release/deployment rules: `<existing guidance when applicable>`.

Only actual applicable user or project authorization permits publication, merge, release or deployment. Task-specific grants are recorded with their source in the task record.
