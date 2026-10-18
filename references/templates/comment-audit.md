# <Task> — comment and documentation audit

- Delivery ID: `<task>.comment-audit.r<n>`
- From: coordinator. To: auditor with fresh context. An agent handoff within the existing authorized task.
- Candidate: `<actual source/artifact identity and relevant inputs>` in `<location>`, compared with `<actual base; full SHAs for Git>`.
- Rules: `<project comment, naming and public/private conventions>`.
- Audit trigger and checkpoint: `<project's PR/MR, release or change-class requirement; scope and execution point>`.
- Finding policy: `<absolute skill path>/references/review-policy.md`; `<project additions and treatment policy>`.

## Scope

Inspect changed comments, documentation, test names and other explanatory text in the diff, plus adjacent claims the change may have invalidated. Product files are read-only; report findings rather than fixing them. Use this separate pass when project rules or the change warrant it.

Pin the audited version and identify any later delta that remains unchecked. Verify suggested corrections against the actual code; this audit does not independently approve changed executable code. Classify findings using the supplied severity policy; a wording preference is not a blocker. Return findings for coordinator disposition rather than automatically requesting repairs or another audit. A text-only audit does not reset or extend the code-review budget. If checks are needed, coordinate with the verification owner and reuse unchanged-input evidence. Stop owned background commands before returning.

Check for:

1. Private planning identifiers, machine paths, credentials or internal links that do not belong in the published artifact. Distinguish these from terms and references the project intentionally exposes.
2. Claims inconsistent with the candidate code, dangling symbols, test names disagreeing with their assertions, misleading change-history narration, redundant commentary and violations of the project's writing conventions.

## Result and return

Write `<task-dir>/review/<delivery-id>.md`: per finding, file:line, quoted text, category, proposed severity, evidence/reason and suggested correction. A proposed blocker also needs its requirement/source, reachable trigger, consequence and resolution criterion. Group documentation findings separately if useful. Include the audited version and summary counts. Keep it immutable after returning.

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
