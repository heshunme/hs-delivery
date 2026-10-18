# Project initialization and recovery

Use this when adopting the skill in a project, repairing incomplete setup, moving the installation or diagnosing failed recovery. Skill discovery, project preparation, host integration and task registration are separate operations. Invocation of the skill is a reason to inspect existing infrastructure, not permission to create it.

## Inspect before proposing changes

Keep the initial inspection read-only. Resolve:

- The target repository and actual checkout/worktree, applicable instructions, existing convention entry, task root and any setup record. An absent `.delivery` is not proof that equivalent infrastructure is missing.
- The installed skill's accessible location and revision. Its checkout is not necessarily the target project.
- The actual harness, version, loaded project instruction sources and current completion capabilities. A model name alone does not identify its harness; CLI, desktop, managed sessions and remote execution can differ.
- The interpreter's absolute path, version, OS and needed standard-library support. Select only the capabilities needed: Markdown workflow, core helpers, or the Codex/Paseo queue path.
- Existing target files and their tracked/ignored state, the Git exclusion file, available package tooling and any configuration that must be preserved.

Classify each needed capability as ready, missing, unsupported or unverified. Repair only relevant gaps. A consultation or brief single-session task can use the Markdown workflow without installing helpers or creating persistent records. Existing project records and conventions may be retained in place.

Participants in an existing delivery use the coordinator-provided accessible convention and task paths. Ignored records need not exist in every worktree; their absence is not a reason to initialize each participant's checkout or duplicate the records.

For a task spanning independent repositories, follow [multi-repository delivery](multi-repo.md). Choose one accessible coordination repository or established record location for the shared convention and task record. Do not initialize `.delivery` in every member repository, and do not select a non-Git aggregate directory merely because it contains all checkouts. Each member still keeps and follows its own repository instructions.

## Resolve project policy before calling setup complete

Use the [project contract](project-contract.md#resolve-delivery-behavior) to inspect actual delivery rules as well as infrastructure. Read repository instructions, hooks, CI and existing decisions first. Fill derivable facts without asking the user to do that investigation. Inherit settled choices and grants with their sources; do not ask for their authorization again.

Present the remaining choices in one compact proposal: the proposed value/default, how it changes delivery, and any unresolved requirement. Include additional blocker conditions, major/minor treatment, recheck requirements for repairs by severity, review-round budget, separate comment audit, UI preview, applicable checks/acceptance, and endpoint/authority. Keep universal resolution and evidence rules distinct from configurable choices. A missing project file does not turn off the skill's defaults.

Resolve each applicable item as inherited, default adopted or project-specific; record inapplicability with a reason. Keep unresolved facts or choices pending with their dependent action and next owner. Do not call delivery policy complete while applicable decisions remain pending. Configuration and dependency installation may finish separately; unrelated work can proceed using established capabilities. Repeated setup asks only about relevant gaps or changed policies, not the whole questionnaire again.

## Show a concrete plan and obtain confirmation

Before writing project files, exclusions, environments or host settings, show the actual intended changes. A useful preview contains:

| Item | What the user reviews |
|---|---|
| Project files | Absolute paths, whether each file is new or edited, and the content or focused diff to apply |
| Delivery behavior | Resolved policy values and sources, recommended defaults and effects, pending choices with their dependent actions and next owners |
| Local exclusion | Resolved exclusion file, exact patterns and the scope across linked worktrees; `.gitignore` is left unchanged |
| Python | Existing probe results, selected interpreter, whether an environment is created, package versions and any network download |
| Host entry | Actual loaded instruction source, appended text, whether the file is tracked and whether a new session or host approval is needed |
| Verification | Local checks to run, live recovery cases still pending and their next owner |

Obtain explicit confirmation of this plan. If equivalent setup work has already been explicitly approved with these concrete actions, carry it out without asking again. Approval to package the skill or use its delivery workflow is not approval to initialize another project. If approval is declined or pending, leave dependent setup unchanged and continue work that can use existing capabilities.

The confirmed scope can include the required dependency installation; do not ask again for each included command. A newly required destination or broader action needs a revised preview and confirmation of that delta. Initialization grants no publication, merge, deployment or automatic task-resumption authority.

## Prepare the project

For a project choosing the default layout, create `.delivery/` and fill:

- `.delivery/delivery.md` from [the project template](../assets/delivery.md), linking established instructions, checks and decisions. Record the resolved policy set and remaining gaps, not just untouched template fields.
- `.delivery/setup.md` from [the local setup template](../assets/setup.md), recording this machine's paths, capability choices, approved changes and verification state. This is an agent-readable receipt, not configuration parsed by helpers or a replacement for authorization sources.
- `.delivery/runs/` as the task root, unless an existing task location is retained. Task directories and cards are created only for real tasks that need continuity.

Record retained alternative locations instead of migrating them. Existing files are merged through focused edits, not replaced by templates. Do not create a sample active task, register an inbox, bind a recipient or start participants/observers as part of basic initialization.

### Keep artifacts locally excluded

Use Git to resolve the paths from the actual target checkout:

```text
git -C <repo> rev-parse --show-toplevel
git -C <repo> rev-parse --path-format=absolute --git-path info/exclude
```

If the installed Git lacks `--path-format`, resolve its `--git-path info/exclude` result relative to the command's working directory. Do not assume `<repo>/.git` is a directory. The exclusion file normally belongs to the common Git directory and is shared by linked worktrees; include that scope in the preview.

When the default layout needs exclusion, append `/.delivery/` to that file once, preserving existing content and a separating newline. Check the effective result with `git check-ignore -v` against an actual untracked artifact; existing repository patterns can override a local exclusion. Reuse an effective existing rule rather than duplicating it. If tracked `.delivery` files exist, report them: exclusions do not stop tracking, and initialization does not remove files from the index.

Any new private host configuration outside `.delivery/` needs its own reviewed exclusion if it should stay untracked. A tracked project instruction edit remains a visible project change. Do not modify `.gitignore`, global exclusion settings or unrelated ignore rules to hide the setup. For a non-Git project, report that local Git exclusion is unavailable rather than initializing Git implicitly.

Git documents [local exclusion and tracked files](https://git-scm.com/docs/gitignore) and [worktree path resolution](https://git-scm.com/docs/git-worktree).

### Select Python capabilities

The Markdown workflow requires no Python environment. Core helpers use standard-library Python 3.9+ on Linux, macOS or WSL; the inbox relies on `fcntl`. Native Windows helper support is not implemented. Record unsupported capabilities and use an agreed supported environment or the Markdown workflow rather than claiming full helper readiness.

Probe a candidate interpreter without installing anything:

```text
<python> -B -c 'import sys, fcntl; print(sys.executable); print(sys.version); assert sys.version_info >= (3, 9)'
<python> -B <skill>/scripts/task_card.py --help
<python> -B <skill>/scripts/task_inbox.py --help
```

Check only the helpers actually needed; `-B` avoids writing import caches during inspection. If core helpers are ready, no package installation or new virtual environment is required. Missing `pip` is not a core-helper failure.

Only the `codex-queue` transport, the default for Codex/Paseo inboxes, needs Python 3.11+, a compatible `websockets` package and a compatible local daemon/CLI. Claude selects `harness` explicitly when it needs an inbox. Follow [the Codex/Paseo adapter](hosts/codex-paseo.md) for protocol checks; an installed library alone does not establish queue or wakeup compatibility.

If this transport is selected, first inspect an existing interpreter or environment and the destination's managed packages. When project policy calls for host-wide availability, prefer the platform package manager after the setup plan is confirmed. For example, on an APT-based host:

```text
apt-cache policy python3-websockets
sudo apt-get install python3-websockets
```

Do not use system-level `pip` in place of the platform package manager. When no compatible managed package exists and project policy permits isolation, reuse a suitable environment or propose `<repo>/.delivery/.venv`, then install the pinned fallback from `<skill>/requirements-queue.txt` with that environment's `pip` or `uv`. These commands illustrate resolved paths; use structured arguments or proper quoting. Do not choose a global or isolated installation implicitly; record the selected ownership. If the planned route is unavailable, preserve the partial result and propose only the necessary adjustment.

Verify the chosen interpreter with `sys.version_info >= (3, 11)`, the installed `websockets` version and ownership, `fcntl`, and either `websockets.asyncio.client.unix_connect` or the compatible top-level `websockets.unix_connect`. Run the queue fixture tests with that interpreter. Record its absolute path and package ownership in `setup.md`. Queue-enabled inbox operations, publishers and observer launchers must all use that interpreter, including across terminals. A task records its actual interpreter/binding; a project setup receipt supplies a candidate to recheck, not proof that another machine or worktree has it.

## Add the host's project instruction entry

Keep these responsibilities distinct:

| Layer | Responsibility |
|---|---|
| Loaded project instructions | State when to use the skill and which files to reread on recovery |
| Skill and project conventions | Define the reusable procedure and stable project-specific rules |
| Task card and linked evidence | Preserve this task's current state, version, outstanding work and authorization sources |
| Automatic memory | Supply optional learned hints; it is not the required project entry or task-state authority |

Fill [the recovery snippet](../assets/recovery-instructions.md) and append it to an instruction source the actual harness loads. On Codex, use the applicable `AGENTS.md` or an already established project instruction mechanism. On Claude Code, use its loaded project `CLAUDE.md` or another explicitly configured project instruction source. Check precedence and loading for that harness rather than assuming these mechanisms have identical authority. See [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and [Claude project instructions versus auto memory](https://code.claude.com/docs/en/memory).

Preserve existing instructions and their scope. Do not create an override that hides the project's rules, overwrite an existing instruction setting or use global configuration or automatic memory merely to install the pointer. If both hosts demonstrably load one shared instruction file, maintain one pointer there. Add only the host actually being adopted; another host is a later incremental setup.

Keep the entry outside the skill, project convention and task history: it must lead back to those files when their bodies have left context. Keep it short and conditional on delivery work. A portable shared instruction can identify `hs-delivery` by name and tell the host to resolve its installed `SKILL.md`; machine-specific absolute paths belong in the local receipt or an explicitly local instruction source. Confirm that the reference resolves on the destination machine. Never assume moving the skill leaves an old absolute pointer valid.

## Record and verify the result

Update the local receipt after each completed setup step. Record **delivery policy resolved** separately from host integration: link the agreed convention source and its confirmation or inherited authority, and list any pending policy gaps with their impact and owner. Installed dependencies and a loaded entry do not establish that delivery behavior has been settled.

Keep three separate integration statuses per host:

- **Configuration written:** the approved files, effective exclusion and relevant Python probes are checked. Existing repository rules remain intact.
- **Entry loaded:** a fresh host session visibly receives the project pointer and resolves the intended skill and conventions. A file existing on disk is not evidence of loading.
- **Recovery verified:** the tested compaction/resume transitions lead to rereading the skill and correct task card while preserving the actual scope and pending work.

Mark live cases pending until exercised through [destination host acceptance](host-acceptance.md). If the user owns that later acceptance, finish authorized setup and local checks now, record its next owner and report the gap. Do not start another session, force compaction or launch workers merely to turn a status green. Root-session success does not prove subagent recovery or a different harness's behavior. A setup receipt is not an active-task selector.

Reinitialization is a read-only comparison followed by a preview of missing or changed setup. Moving machines, changing harnesses or replacing an interpreter invalidates the affected observations. Do not overwrite complete setup or repeat installation solely because the skill was invoked again. On partial failure, retain the outcome and repair or remove only changes owned by this setup; do not restore whole shared files over intervening edits or delete existing records/environments.

## Recover an active task

Read the project's conventions and applicable repository rules, then reload this skill. Resolve the actual task root from those conventions; the fallback is `<repo>/.delivery/runs`. Use the selected helper interpreter if available; a missing helper environment does not prevent reading the Markdown records.

```text
<python> <skill>/scripts/task_card.py list --runs <runs-dir>
<python> <skill>/scripts/task_card.py show --task-dir <active-task-dir>
```

Match the current user request and known session/worktree assignment to the task's goal, endpoint and authorization before continuing. With multiple active cards, use their goals and linked plans; do not pick one merely because it is newest. If the mapping remains ambiguous, ask which task to resume before dependent action. `list` only finds immediate child records with a task card. An empty list does not prove that older, differently located or cardless project records are absent. Follow known task links before creating a card when one is needed.

Reconcile candidate inputs, participant identities, actual review coverage, consumed review rounds, repair policy, finding dispositions, pending results/decisions and owned observers. Recover the round history before dispatching; missing counts do not authorize resetting the budget. Use inbox `status` to inspect first; `take` and other state transitions are task operations. Respect an explicit pause or stop and the current user's resumption authority. A stale active card is context to reconcile rather than permission to relaunch its workers.

Replace the current card through `task_card.py set` after a meaningful handoff or decision. Keep fixes and corrections in the history below it. Preserve old observations' tested versions; do not treat the compaction summary or setup receipt as a newer authority than the actual records.

Choose the actual [Codex/Paseo](hosts/codex-paseo.md) or [Claude Code](hosts/claude-code.md) completion path. Record whether it delivers results only in an active turn, wakes an idle coordinator or requires explicit resumption. A harness ledger records results but sends no wakeup. Mark unexecuted host cases pending or inapplicable with a reason; package-local protocol tests do not establish destination-host behavior.
