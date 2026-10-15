# Project-specific delivery conventions

Read the target project's existing rules and accepted task first. A small `.ai_docs/delivery.md` may fill gaps for repeated use, but adoption does not require creating it. Link existing sources; keep a rule in one maintained place.

Recover these facts for the current task:

| Area | Information needed |
|---|---|
| Context | Planning index, accepted decisions, design principles, current task record |
| Checks | Cheap iteration checks, full gates, hook coverage, conditional lanes/platforms, relevant commands |
| Review | Review guidance, required independence and any separate comment audit |
| Environment | Isolation recipe, data/device limits, shared resource locks and test prerequisites |
| Records | Task root, evidence locations, private/public boundaries, existing finding or flaky-test log |
| Publication | PR conventions, permitted delivery endpoint and applicable authorization sources |

Use repository instructions and actual scripts to establish check coverage. Another project's hook behavior, platform matrix, retry allowance, commit style or permission grant does not carry over.

For a project without conventions, make ordinary choices proportionate to the change and record the ones needed for continuity. Ask only about missing decisions that materially affect the authorized work. Keep an approval-dependent action pending while doing unblocked preparation.

## Paths and installation

- `<skill>` is the directory containing this skill's `SKILL.md` and scripts.
- `<repo>` is the target repository; helper installation location does not identify it.
- `<task-dir>` is the project's actual task record directory.
- `.ai_docs/runs/<task>/` is a fallback convention, not a requirement to reorganize an existing project.

Use absolute paths in assignments that cross worktrees or sessions. Do not copy machine-specific inbox state or observer bindings as part of installing the skill elsewhere. Keep private records out of published output; describe the behavior there in self-contained terms.
