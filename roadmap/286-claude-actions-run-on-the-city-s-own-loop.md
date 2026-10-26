# 286. Resume, New, Stop and the other claude actions wait on the city's own loop

**Open, in progress since 2026-10-26 in the session "item 286". Filed 2026-10-26 (r1122), the follow-up item 284 named. Nobody's call — a defect not yet seen, by the same mechanism as item 284.**

Item 284 moved copy, copy path, reveal and open pull request beside the city's loop, because waiting on a clipboard tool froze the whole map.
The actions that run `claude` still wait on the loop: Resume, New, Fork, Stop, Remove (demolish) and Restore.
`Game.act` (`pkg/render/keys.go`) calls `actor.Do` synchronously for them; they reach `execRunner.Run` (`pkg/control/control.go`), which uses `cmd.Output()` with a stderr buffer, so it waits for both pipes to close, with `context.Background()` from `pkg/commands/city.go` and no deadline.
If `claude --bg` or anything it starts keeps a pipe open, or `claude` stalls on the network or a lock, the map stops: no frames, no input, no quit.

## The fix

1. Give `Run` a `WaitDelay` and a deadline per verb, long enough for a real resume.
2. Move these actions beside the loop through the set item 284 adds, with their results, including New's and Resume's notices, coming back as notices; keep move, mute, review and close-up synchronous, since they write the groups file in order.
3. Restore resumes several sessions in a loop: it runs beside the loop as one job, reporting each.
4. Tests, data-driven over each verb: a `claude` that never exits returns at its deadline with a notice; a `claude` whose child holds the pipe returns once `claude` exits; the city keeps drawing while each runs.
