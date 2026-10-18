# Review the accepted behavior

Read this for an independent review, with the project's review and design rules and [finding severity and convergence](review-policy.md). A project guide adds subsystem-specific checks; its absence does not remove this baseline. Scale depth to the change without presenting a sample as complete coverage.

## Establish scope and expectations

Identify the actual comparison base, candidate and relevant local inputs. Resolve the base from the task and repository rather than assuming a branch name. Read the entire assigned diff, including deletions, renames, generated files, migrations, tests, configuration, guard scripts and documentation. Follow affected callers and dependencies where needed to assess behavior. State any unread or unavailable scope.

Establish the caller, observable problem, accepted behavior and constraints. Separate accepted requirements, assumptions and unresolved decisions. The current implementation and a reviewer's preference are not requirements. Reopen an accepted decision only when concrete evidence shows it cannot hold.

## Follow the operation through its lifecycle

Trace a real operation from its UI, CLI or machine entry through input/contracts, authoritative state and side effects, response/events, consumer recovery and the observable result. Use the layers the change actually has. At least explain the successful path.

For each important state, identify its writer, identity, ordering, storage, propagation and terminal state. Check cancellation, retries after lost responses, concurrent or late writes, and restart/disconnection recovery when the accepted behavior or reachable code makes them relevant. Confirm that success means the stage actually completed, and that consumers have the information needed for their next action.

Inspect affected boundaries: contract semantics and consumers, data ownership and migrations, error propagation and cancellation, cleanup, and cost as data grows. Read generated migration output rather than treating generation as proof. Tie complexity, dependencies and performance concerns to actual supported scenarios; do not invent speculative requirements or numerical performance gates.

## Check replacement and safeguards

For a refactor or replacement, trace old symbols, entry points and consumers. Decide whether old interfaces, branches, stored state, helpers, tests, docs and guard scripts still serve the current model. Search results locate evidence; they do not alone prove code unreachable.

Preserve valid behavior guarantees while updating tests tied to obsolete internals. Check whether guard scripts cover new entry points and whether test names match fixtures and assertions. Read affected explanatory text, including adjacent comments made false by the change. Public explanations must stand on their own without private planning vocabulary; removing a marker does not resolve the issue it referred to.

## Return an actionable conclusion

Give each finding a concrete trigger, code location, evidence, consequence and requirement source. Distinguish reproduction, code-path proof, inference and an unanswered question. Use the severity and disposition rules before recommending a repair.

Report the actual reviewed inputs, covered behavior, checks/evidence reused or run, and remaining limitations. Passing tests do not establish unexamined behavior. Later rounds inspect the approved repairs and their interaction with the earlier candidate; use the convergence rules rather than restarting a full review to find more work.
