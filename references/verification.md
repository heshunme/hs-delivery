# Verification budget

Use this when planning checks or assigning a writer/reviewer. The target project's scripts, hooks and CI define its gates; this page supplies the evidence and scheduling rules.

## Establish coverage

Read applicable repository guidance and scripts. Identify cheap iteration checks, the full local gate, what the commit hook already runs, extra behavior/platform lanes and remote required checks. Put actual commands and applicability in the assignment or link the project contract. Do not assume a hook runs tests or that CI covers a manually triggered platform suite.

For substantial changes, assign one expensive-verification owner and execution point. Serialize work sharing mutable inputs, caches or bottlenecks. Separate worktrees alone do not establish cache or machine isolation. Use the project's existing lock when appropriate; choose and record a task lock only when one is needed.

Check the actual tool scan roots: a nested worktree can enter its parent's lint, test or file scans even when Git considers it separate. Before parallel execution, establish exclusions or use a task-owned location outside those scans without weakening repository guards. Separate scheduling/lock wait from execution time when interpreting measurements.

When several branches contribute to one delivery, plan which full checks can run once on a stable combined candidate rather than once per branch per checkpoint and again after integration. Preserve required per-branch/PR gates, platform checks and evidence for the actual versions that will ship. Combination evidence does not automatically cover independently published branches; name the coverage and execution point before assigning commands.

## Budget per candidate

1. During iteration, use checks that answer the current uncertainty: affected tests, relevant static checks and package/type checks where applicable.
2. Run each required full gate once on the stable candidate, accounting for gates already run by hooks. Add the conditional lanes the change touches.
3. Reuse a passing result for unchanged [relevant inputs](task-record.md#candidate-inputs-and-retention), including configuration, data, dependencies and artifacts when material. A rebase to an identical tree or a message-only amendment may reuse evidence; record the original tested identity and rationale. An unchanged SHA does not establish that other inputs stayed the same.
4. For a later delta, assess which behavior, dependencies and environments it can affect. Run the required and affected checks. Documentation-only work may still have build or link checks.
5. Preserve required hooks. Use an exemption only when the target project or user explicitly supplies it, including any replacement checks it requires.

Assignments name the actual checks. A blanket demand to run every available suite adds no coverage argument.

The implementer, reviewer and acceptance templates carry the short verification rules themselves. Preserve those lines in dispatched assignments; replace only project-specific parameters. A worker should not need the coordinator's transcript to learn about duplicate gates, failure classification or stable candidate inputs.

## Failures

Classify a red run before rerunning: candidate defect, environment/tool failure or suspected flake. Retain the failure's version, logs, conditions and method.

For a suspected unrelated flake, use a focused reproduction and the project's bounded retry policy. If none exists, start with one focused rerun and report unresolved uncertainty before buying another expensive full run. A passing rerun alone does not establish a cause. Repair a post-test message or packaging refusal at that stage rather than automatically rerunning tests that already passed on unchanged inputs.

Record skipped, blocked and unexecuted gates explicitly. A local result cannot silently substitute for a required remote or platform check. Skill-only edits use relevant structural, link, loading and helper checks rather than the target application's entire suite.
