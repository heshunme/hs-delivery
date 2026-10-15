# HS Delivery

A portable software-delivery skill extracted from the local `buffin-delivery` workflow. This repository is an independent starting copy for iteration; it does not modify or track the source project's private plans, evidence or authorization grants.

The repository root is the skill directory: start at [SKILL.md](SKILL.md). The package contains workflow references, four assignment templates, task-record/inbox helpers and optional host observers. Project rules and check commands remain in the target repository; see the [project contract](references/project-contract.md).

The project convention entry point is `.delivery/delivery.md`; the fallback task record is `.delivery/runs/<task>/task.md`. A [starter delivery.md](assets/delivery.md) describes the expected project-specific content, and a [local setup receipt](assets/setup.md) records destination-machine integration separately. Existing equivalent project structures can be retained.

## Use on another machine

Copy or clone this whole directory into the host's configured skill-discovery location, keeping the folder name `hs-delivery`. An existing checkout can also be linked there. Confirm actual discovery on the destination host; a skill checkout and the project using it are separate locations.

For first use in a project, follow [project initialization and recovery](references/setup-and-recovery.md). Inspect existing infrastructure without writing, show the actual file/configuration changes and dependency needs, then obtain the user's confirmation before applying setup. The default layout contains `.delivery/delivery.md`, `.delivery/setup.md` and a `runs/` task root. Add a local Git exclusion for `/.delivery/` without editing `.gitignore`; retain existing rules and equivalent record locations. A consultation or brief task can use the Markdown workflow without creating persistent infrastructure.

After confirmation, adapt the [recovery instruction snippet](assets/recovery-instructions.md) for a project instruction source the actual harness loads. Project instructions, automatic memory and task cards serve different roles. Record the interpreter and integration details in the local receipt; distinguish configuration written, entry loaded and recovery verified. Live compaction/resume acceptance can remain visibly pending for the user's later trial. Setup creates no artificial active task or inbox and launches no workers.

The Markdown workflow can be used without running helpers. Python helpers require Python 3.9+ on Linux, macOS or WSL. Inbox locking uses `fcntl`; native Windows helper support is not implemented. Task artifacts live in the target project, separate from this installation.

Paseo-managed Codex participants return results through an inbox with the default `codex-queue` transport, which wakes the waiting coordinator. Claude and built-in Codex subagents use native hand-backs within their documented lifecycle. Claude explicitly selects `--transport harness` when it needs an inbox; that ledger sends no messages and relies on the host's completion path.

Core helpers need no third-party packages or new environment when a suitable interpreter already exists. The default inbox transport, `codex-queue`, requires Python 3.11+, a compatible `websockets` package, a compatible local Codex daemon/CLI and a recipient kept available by its host. It connects directly to the local Unix WebSocket in Python. Install this dependency for the Codex/Paseo inbox path; Markdown-only, core-record and explicit harness-inbox use do not require it. A compatible managed system package can provide it when destination policy calls for host-wide availability; `requirements-queue.txt` pins the isolated-environment fallback.

Use the selected interpreter's absolute path for queue-enabled inbox operations, publishers and observer launchers across host terminals. Record local readiness in the setup receipt and the task's actual binding in its record. Core record and harness-inbox helpers can still run on standard-library Python without this package.

Read the [Codex/Paseo host reference](references/hosts/codex-paseo.md) before using that delivery path. The queue adapter is version-sensitive and must be checked on the destination machine. Historical private experiments were not copied as portable proof of host behavior.

## Local validation

```bash
python3 -m unittest discover -s tests -v
```

Without a compatible `websockets` package, the same command runs the core checks and skips queue-connection tests. Queue tests use a disposable local Unix WebSocket server. Checks do not contact GitHub or a real agent session, publish messages, or modify another project. Live delivery and host completion on another machine still need an actual trial.

The [destination host acceptance checklist](references/host-acceptance.md) is prepared for that later trial and remains unexecuted. It covers fresh discovery, compaction/resume, participant handoffs, idle completion, interruption and resource closeout. Local tests and this documentation do not claim those host scenarios passed.
