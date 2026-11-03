# 341. `botropolis rm` gives up when Claude Code has no job for the session, so a stopped session cannot be demolished

**Fixed 2026-11-03 (`c26c509`, r1257). Filed 2026-11-03 (r1256), from 0.4.0's L2 check. Nobody's call — a defect; whether it gates 0.4.0 is Aria's.**

With Claude Code 2.1.310, `claude stop` removes a background job from `claude agents --all` outright (0.3.4's CLI kept stopped jobs).
`botropolis rm <id>` on such a session then fails — *claude rm: exit status 1: No job matching '<id>'* — and the session stays in the daemon as resting: `pkg/commands/sessions.go` (about line 172) returns on `claude rm`'s error before it forgets the session.
So a session the CLI has already dropped cannot be demolished from Botropolis at all, from `status --live`, the card or the CLI.

## The fix

When `claude rm` says there is no such job, `rm` goes on to forget the session (the daemon and the ledger), and says the CLI had already dropped it; any other `claude rm` error still stops it.
Tests in `pkg/commands` for both, and L2 re-run against the next release.

## Closed

`control.Remove` now reports claude rm's *No job matching* as `control.ErrNoJob`.
`Sessions.Remove` carries on past it, forgets the session through the daemon and the ledger, and the CLI says on stderr that Claude Code had already dropped it.
Every other claude rm error still stops the remove.
`pkg/commands/rm_dropped_test.go` covers both, with a stubbed claude runner behind the real `control.Control` (`c26c509`, lint fix `f286a50`, r1258).

Not covered, for Aria: a remove *by job id* of a dropped job still forgets nothing, because the job id's session is looked up from Claude Code, which no longer has it.
The card and `status --live` remove by session id, so they are unaffected.
L2 is still to be re-run against the next release.
