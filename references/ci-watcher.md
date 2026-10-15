# Continue after external CI without model polling

Use this only for an authorized task's existing GitHub Actions run. Choose the host's completion mechanism: [Codex and Paseo](hosts/codex-paseo.md#finite-observers) use the finite Python observer with a `codex-queue` inbox; [Claude Code](hosts/claude-code.md#long-commands-and-ci) can use native background Bash directly, with no workflow-imposed timeout. Both retain the tested version and reconcile actual results after the callback. Ordinary short commands keep their normal completion path.

The remaining sections apply when choosing `watch_ci.py`, which is optional on Claude. It uses installed `gh`, reads run state at intervals and publishes a durable result to the registered task inbox when observation ends. It creates no agent, workflow run, PR edit or merge. Its own finite budget does not impose a time limit on the native Bash path.

## Bind and launch

1. Register the coordinator and its [task inbox](result-inbox.md) in the task. The recipient must belong to this task and remain available in its original host.
2. Read `gh api repos/OWNER/REPO/actions/runs/RUN_ID`. Pin the actual `id`, `run_attempt` and full `head_sha`. Use a fresh state directory for this observer, such as `<task-dir>/evidence/watch-<run>-<attempt>/`. A rerun of the same run ID changes its attempt and needs reconciliation.
3. Launch the observer as a process whose lifetime is independent of a model turn, as the host reference describes. Do not assume an unawaited promise, an arbitrary `&` or a yielded tool call installs a durable callback.
4. Run the command below with the actual registered values. Choose the interval and finite budget for the run; defaults are 60 seconds and two hours. Pass `--thread` only for a `codex-queue` inbox.

```text
exec python3 <skill>/scripts/watch_ci.py
  --task <task-id> --repo <owner/repo> --run-id <id> --attempt <attempt>
  --sha <full-sha> [--thread <coordinator-native-uuid>] --mailbox <registered-inbox>
  --state-dir <absolute-state-directory> --interval 60 --max-wait 7200
```

5. Confirm `ready.json` or an already-finished `result.json`, plus the host process state. `binding.json` alone means launch intent, not a working observer; old `ready.json` alone cannot prove continued liveness. If startup fails, resolve or record the failure before promising automatic continuation.
6. When there is no useful independent work left, record the pending gate, observer and next owner, tell the user that continuation is arranged, then run inbox `wait`. Process a returned ready batch; end the turn normally only after it reports `waiting`. Do not remain in a model sleep/poll loop, interrupt the thread, archive its workspace or call the delivery complete. Host progress-message requirements apply while actively working, not by inventing more active waiting turns.

## Consume and stop

The observer writes `latest.json`, `status.json` and an immutable `result.json`; the outbox contains the result publication receipt. A `recorded` observer status is durable publication, not a separate notification or model acknowledgment. Each binding has a unique observer ID in its delivery ID, so a later resumed observation of the same run can report a new result without being mistaken for replay. It publishes for completed runs regardless of conclusion, a changed SHA/attempt, three consecutive query errors, and its monitoring deadline. CLI/API failure is `monitor_error`, not a failed CI result. Publication failure leaves `notification_uncertain` and no automatic retry. No model runs during polling.

On notification, the coordinator validates task membership, delivery ID, artifact hash, run identity and current candidate, then reads fresh remote state. A successful run is evidence for its pinned version only. Collect relevant job logs on failures; reconcile the full set of required checks before closing delivery. The coordinator takes the inbox batch and acknowledges each handled ID locally. Do not acknowledge back to scripts or repeat effects for an already-handled ID. An observer can also end without publishing: stopped, `notification_uncertain`, or refused at startup. When its process is gone but the inbox has no result for it, read its `status.json` and reconcile the open gate instead of waiting for a wakeup that will not come.

To stop or supersede an observer, create its `STOP` file or signal it through the host, then inspect its final status. A stop observed while gathering the result records `stopped` and suppresses publication; it does not cancel GitHub Actions. A stop detected during result handoff retains the result and may record `notification_uncertain`. A published result or already-started input may remain after STOP: the coordinator must dispose of an obsolete task/version through the inbox. Stop and reconcile before archiving the owner, and confirm the observer's host resource is gone as the host reference describes. Do not rerun an existing state directory or delete an uncertain intent to retry.

`watch_cmd.py` and `watch_result.py` reuse this lifecycle through `scripts/observer.py` for long local commands and expected participant results on a host without completion callbacks; the [Codex host reference](hosts/codex-paseo.md#finite-observers) gives their launch. This is a finite local process, not a restart-safe service. Machine shutdown, SIGKILL or loss of its host process may stop it without a callback. Reconcile the recorded observer and latest run when resuming; start a new binding only after checking the old observer and outbox. No automatic session restore or scheduler is installed.
