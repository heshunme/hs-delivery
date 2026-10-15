# <Task> — comment and documentation audit

- Delivery ID: `<task>.comment-audit.r<n>`
- From: coordinator. To: auditor with fresh context. An agent handoff within the existing authorized task.
- Candidate: `<full sha>` in `<worktree>`, compared with `<base full sha>`.
- Rules: `<project comment, naming and public/private conventions>`.

## Scope

Inspect changed comments, documentation, test names and other explanatory text in the diff, plus adjacent claims the change may have invalidated. Product files are read-only; report findings rather than fixing them. Use this separate pass when project rules or the change warrant it.

Check for:

1. Private planning identifiers, machine paths, credentials or internal links that do not belong in the published artifact. Distinguish these from terms and references the project intentionally exposes.
2. Claims inconsistent with the candidate code, dangling symbols, test names disagreeing with their assertions, misleading change-history narration, redundant commentary and violations of the project's writing conventions.

## Result and return

Write `<task-dir>/review/<delivery-id>.md`: per finding, file:line, quoted text, category, evidence/reason and suggested correction. Group documentation findings separately if useful. Include the audited version and summary counts. Keep it immutable after returning.

```text
Result: <delivery-id>
Artifact: <absolute result path>
SHA-256: <artifact digest>
Version: <audited-version>
Verdict: <counts and consequence>
Decisions needed: <none, or specific decisions>
```

For an inbox return, publish before ending the round:

```text
python3 <skill>/scripts/queue_result.py --task <task-id>
  --delivery-id <delivery-id> --sender comment-auditor --artifact <absolute result>
  --version <audited-version> --summary <counts>
  --outbox <task-dir>/outbox-comment-audit --mailbox <registered-inbox>
  [--thread <registered-native-uuid, codex-queue only>]
```
