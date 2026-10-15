# HS Delivery

A portable software-delivery skill extracted from the local `buffin-delivery` workflow. This repository is an independent starting copy for iteration; it does not modify or track the source project's private plans, evidence or authorization grants.

The repository root is the skill directory: start at [SKILL.md](SKILL.md). The package contains workflow references, four assignment templates, task-record/inbox helpers and optional host observers. Project rules and check commands remain in the target repository; see the [project contract](references/project-contract.md).

## Use on another machine

Copy or clone this whole directory into a location your agent loads skills from, keeping the folder name `hs-delivery`. For Codex, the default skill location is `~/.codex/skills/hs-delivery`. An existing checkout can also be linked into the host's skill directory. This repository does not install itself or change agent configuration.

The Markdown workflow can be used without running helpers. Python helpers require Python 3.9+ on Linux, macOS or WSL. Inbox locking uses `fcntl`; native Windows helper support is not implemented. Task artifacts live in the target project, separate from this installation.

Native hand-backs are the first choice for participant results. A `harness` inbox is a local ledger and sends no messages; automatic continuation depends on the host's completion support.

The optional `codex-queue` transport additionally requires Node.js, the `ws` dependency, a compatible local Codex daemon/CLI and a recipient kept available by its host. Install the Node dependency from this directory with:

```bash
npm ci --ignore-scripts
```

Read the [Codex/Paseo host reference](references/hosts/codex-paseo.md) before opting in. The queue adapter is version-sensitive and must be checked on the destination machine. Historical private experiments were not copied as portable proof of host behavior.

## Local validation

```bash
python3 -m unittest discover -s tests -v
node --test tests/queue_bridge.test.cjs
```

The Node test needs the optional dependency and uses a disposable local server. Checks do not contact GitHub or a real agent session, publish messages, or modify another project. Live delivery and host completion on another machine still need an actual trial.
