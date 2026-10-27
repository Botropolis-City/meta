# 286. Resume, New, Stop and the other claude actions wait on the city's own loop

**Fixed 2026-10-27 (`26fe64a`, r1160). Filed 2026-10-26 (r1122), the follow-up item 284 named. Nobody's call — a defect not yet seen, by the same mechanism as item 284.**

Item 284 moved copy, copy path, reveal and open pull request beside the city's loop, because waiting on a clipboard tool froze the whole map.
The actions that run `claude` still wait on the loop: Resume, New, Fork, Stop, Remove (demolish) and Restore.
`Game.act` (`pkg/render/keys.go`) calls `actor.Do` synchronously for them; they reach `execRunner.Run` (`pkg/control/control.go`), which uses `cmd.Output()` with a stderr buffer, so it waits for both pipes to close, with `context.Background()` from `pkg/commands/city.go` and no deadline.
If `claude --bg` or anything it starts keeps a pipe open, or `claude` stalls on the network or a lock, the map stops: no frames, no input, no quit.

## The fix

1. Give `Run` a `WaitDelay` and a deadline per verb, long enough for a real resume.
2. Move these actions beside the loop through the set item 284 adds, with their results, including New's and Resume's notices, coming back as notices; keep move, mute, review and close-up synchronous, since they write the groups file in order.
3. Restore resumes several sessions in a loop: it runs beside the loop as one job, reporting each.
4. Tests, data-driven over each verb: a `claude` that never exits returns at its deadline with a notice; a `claude` whose child holds the pipe returns once `claude` exits; the city keeps drawing while each runs.

## Answered while building

- **The plan's five questions** (manager, 2026-10-26): deadlines of 2 minutes for new, resume and fork, 30 s for stop and rm, 20 s for listing agents, and a 1 s wait delay, set in `pkg/control` so the CLI shares them; starting a session and close-up also run beside the loop, with every groups-file load and save in `commands.Actor` behind one mutex so no move is lost; one action in flight per session and verb, a second press saying it is already running, since a second resume spends twice; and *resuming <title>…* shows while one runs, with no success notice, since the building changing is the answer.

## Closed

Fixed in seven commits ending at `26fe64a` (r1160), on top of items 284 and 291.

- Every `claude` call has a deadline by verb, and one that runs out says *claude <verb> did not answer within <N>* (`pkg/control/deadline_test.go`).
- `Run` waits a second after `claude` exits, then takes what it printed, so a session holding the pipe no longer holds the caller (`pkg/control/exec_test.go`: before the fix, both cases waited out the child's 30 seconds).
- Resume, New, start a session, Fork, Stop, Remove and Restore run beside the loop, once at a time per session and verb, with *resuming <title>…* while they run, cleared on success and replaced by a failure (`pkg/render/claudeact_test.go`).
- Close-up runs beside the loop too: its panel stays open saying *closing up…*, and the city quits through item 291's flag once it completes, not on the key press (`pkg/render/closeup_test.go`).
- Every groups-file load and save goes through one lock; concurrent starts and moves lost about half their writes without it (`pkg/commands/groupslock_test.go`).
- Restore resumes every session it can and names each it cannot (`pkg/commands/restore_test.go`).

Deviation from the fix as written, settled by the manager: start a session and close-up moved beside the loop rather than staying on it, since both run `claude`.
No frame was filmed; the change is in when the footer speaks, not in what the map draws.
