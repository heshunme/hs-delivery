<!-- Fill <skill-dir> with the installed skill's actual accessible location, then append
     this block to the target host's persistent project instructions. Preserve existing rules.
     This file is a snippet, not an automatically installed startup hook. -->

During software delivery using hs-delivery:

- At task start, and after context compaction or session resumption, read `<skill-dir>/SKILL.md`, the applicable repository instructions and `<repo>/.delivery/delivery.md` when present before continuing delivery work.
- Recover the active task from the project's configured task records (fallback: `<repo>/.delivery/runs/<task>/task.md`). Use `<skill-dir>/scripts/task_card.py list --runs <runs-dir>` and `show --task-dir <task-dir>` for cards. An empty list does not establish that older/cardless records are absent.
- Reconcile the card's actual candidate, review coverage, owners, expected results, current authorizations and next action with the linked evidence. Preserve the current user's requested endpoint and any explicit pause/stop.
- Reload the relevant assignment, verification and host references before dispatching another round. Replace the current task card through `task_card.py set`; append historical observations below it.
- Planning, explanations and brief edits retain their narrower scope. The recovery pointer supplies no publication, merge or deployment authorization.
