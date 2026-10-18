# Review the accepted behavior

Read this for an independent review, with the project's review and design rules and [finding severity and convergence](review-policy.md). A project guide adds subsystem-specific checks; its absence does not remove this baseline. Scale depth to the change without presenting a sample as complete coverage.

## Establish scope and expectations

Identify the actual comparison base and [candidate inputs](task-record.md#candidate-inputs-and-retention). Resolve the base from the task and repository rather than assuming a branch name. Inventory the whole assigned change, including deletions, renames, generated files, migrations, tests, configuration, guard scripts, documentation and non-text artifacts. Full review means complete coverage with a method appropriate to each artifact:

- Read handwritten code and explanatory text closely, following affected callers and dependencies where needed.
- For generated output, inspect the source/generator changes, regeneration consistency and consequential output semantics. Large mechanical output need not receive line-by-line reading; generation alone does not establish correctness, especially for migrations and compatibility changes.
- For binaries, datasets and other non-text artifacts, use relevant manifests, semantic comparisons, integrity checks or representative inspection with a stated rationale and limits. A sampled inspection is not exhaustive validation of every value.

Report each category's coverage method and any unavailable scope. Do not silently omit a category because the usual text diff cannot show it.

Establish the caller, observable problem, accepted behavior and constraints. Separate accepted requirements, assumptions and unresolved decisions. The current implementation and a reviewer's preference are not requirements. Reopen an accepted decision only when concrete evidence shows it cannot hold.

## Follow the operation through its lifecycle

Trace an input or trigger through the changed contracts, transformations, relevant state or side effects, and consumers to the delivery's observable result. This may be an interaction, library call, compilation, batch job, data transformation or infrastructure change. Use the stages the change actually has; a pure function needs no invented service lifecycle. At least explain the successful path.

For each important state, identify its writer, identity, ordering, storage, propagation and terminal state. Check cancellation, retries after lost responses, concurrent or late writes, and restart/disconnection recovery when the accepted behavior or reachable code makes them relevant. Confirm that success means the stage actually completed, and that consumers have the information needed for their next action.

Inspect affected boundaries: contract semantics and consumers, data ownership and migrations, error propagation and cancellation, cleanup, and cost as data grows. Read generated migration output rather than treating generation as proof. Tie complexity, dependencies and performance concerns to actual supported scenarios; do not invent speculative requirements or numerical performance gates.

## Check replacement and safeguards

For a refactor or replacement, trace old symbols, entry points and consumers. Decide whether old interfaces, branches, stored state, helpers, tests, docs and guard scripts still serve the current model. Search results locate evidence; they do not alone prove code unreachable.

Preserve valid behavior guarantees while updating tests tied to obsolete internals. Check whether guard scripts cover new entry points and whether test names match fixtures and assertions. Read affected explanatory text, including adjacent comments made false by the change. Public explanations must stand on their own without private planning vocabulary; removing a marker does not resolve the issue it referred to.

## Return an actionable conclusion

Give each finding a concrete trigger, code location, evidence, consequence and requirement source. Distinguish reproduction, code-path proof, inference and an unanswered question. Use the severity and disposition rules before recommending a repair.

Report the actual reviewed inputs, covered behavior, checks/evidence reused or run, and remaining limitations. Passing tests do not establish unexamined behavior. Later rounds inspect the approved repairs and their interaction with the earlier candidate; use the convergence rules rather than restarting a full review to find more work.
