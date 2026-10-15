# Set up discovery and recovery

Use this when adopting the skill in a project, changing its installation or diagnosing a failed resumption. Installing a skill makes it discoverable; a separate persistent entry tells the host to reload it after its body leaves context.

## Install the persistent entry

1. Locate the installed skill's actual `SKILL.md`, the target repository and its project conventions. Fill the paths in [the recovery instruction snippet](../assets/recovery-instructions.md).
2. Append the filled snippet to the target project's already-loaded instructions, preserving existing rules. On Codex this can be the applicable `AGENTS.md` or an existing project startup-instruction mechanism. On Claude Code use its loaded `CLAUDE.md` or existing persistent project instructions/memory. If both hosts already read one shared instruction file, keep one maintained pointer there.
3. Keep the pointer outside `SKILL.md`, `.delivery/delivery.md` and task history: those files are what the pointer must lead the host back to. Avoid replacing repository instructions, writing an override that hides them or changing global configuration solely to install this workflow.
4. Confirm the filled entry actually appears in a fresh host session. Compaction/resume retention requires a later host trial; file existence alone does not prove it. Record the chosen instruction source in `.delivery/delivery.md` and any local interpreter/host binding in the task record.

This package supplies instructions and a snippet; it does not edit another project's startup files or install hooks automatically. Within authorized setup work, make the concrete project change through its existing instruction mechanism. A task that only requests packaging stops at the portable artifacts.

## Recover an active task

Read the project's conventions and applicable repository rules, then reload this skill. Resolve the actual task root from those conventions; the fallback is `<repo>/.delivery/runs`.

```text
python3 <skill>/scripts/task_card.py list --runs <runs-dir>
python3 <skill>/scripts/task_card.py show --task-dir <active-task-dir>
```

Match the current user request to the task's goal, endpoint and authorization before continuing. With multiple active cards, use their goals and linked plans to identify the task; do not pick one merely because it is newest. `list` only finds immediate child records with a task card. An empty list does not prove that older, differently located or cardless project records are absent. Follow known task links and recover their actual state before creating a card when one is needed.

Reconcile candidate inputs, participant identities, review coverage, pending results/decisions and owned observers. Use inbox `status` to inspect first; `take` and other state transitions are task operations. Respect an explicit pause or stop and the current user's resumption authority. A stale active card is context to reconcile rather than permission to relaunch its workers.

Replace the current card through `task_card.py set` after a meaningful handoff or decision. Keep fixes and corrections in the history below it. Preserve old observations' tested versions; do not treat the compaction summary as a newer authority than the actual records.

## Host validation boundary

Choose the actual [Codex/Paseo](hosts/codex-paseo.md) or [Claude Code](hosts/claude-code.md) completion path. Record whether it delivers results only in an active turn, wakes an idle coordinator or requires explicit resumption. A harness ledger records results but sends no wakeup.

Use [the host acceptance checklist](host-acceptance.md) for a destination-machine trial. Mark unexecuted cases as pending or inapplicable with a reason; do not infer host behavior from this package's local protocol tests. The user may own this later acceptance while implementation and local checks finish now.
