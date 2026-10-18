<!-- Adapt the actual convention and task paths, then append this block to the host's
     loaded project instructions after setup confirmation. Preserve existing rules.
     A shared entry resolves hs-delivery by name; absolute machine paths belong in a
     local setup record or an explicitly local instruction source. -->

During software delivery using hs-delivery:

- At task start, and after context compaction or session resumption, resolve the installed `hs-delivery` skill and read its `SKILL.md`, the applicable repository instructions and `.delivery/delivery.md` when present before continuing delivery work. Paths beginning `.delivery/` are relative to the actual target repository.
- If project setup is missing or incomplete, follow the skill's setup-and-recovery reference: inspect read-only, preview concrete changes and obtain the user's confirmation before applying them. Existing equivalent infrastructure and narrower consultation/brief-task scope are retained.
- Recover the active task from the project's configured task records (fallback: `.delivery/runs/<task>/task.md`). Use the selected helper interpreter with `<skill-dir>/scripts/task_card.py list --runs <runs-dir>` and `show --task-dir <task-dir>`, or read the Markdown directly if helpers are unavailable. Match the actual request/session to a task; do not choose the newest card. An empty list does not establish that older/cardless records are absent.
- Reconcile the card's actual candidate inputs, reviewed version, repair recheck policy, declared review units and their consumed/maximum rounds, finding dispositions, owners, expected results, current authorizations and next action with the linked evidence. A new session or retroactive split does not reset a budget. Preserve the current user's requested endpoint and any explicit pause/stop.
- Reload the relevant assignment, verification and host references before dispatching another round. Replace the current task card through `task_card.py set`; append historical observations below it.
- Planning, explanations and brief edits retain their narrower scope. The recovery pointer supplies no publication, merge or deployment authorization.
