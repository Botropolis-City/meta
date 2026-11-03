# 341. `botropolis rm` gives up when Claude Code has no job for the session, so a stopped session cannot be demolished

**Open. Filed 2026-11-03 (r1256), from 0.4.0's L2 check. Nobody's call — a defect; whether it gates 0.4.0 is Aria's.**

With Claude Code 2.1.310, `claude stop` removes a background job from `claude agents --all` outright (0.3.4's CLI kept stopped jobs).
`botropolis rm <id>` on such a session then fails — *claude rm: exit status 1: No job matching '<id>'* — and the session stays in the daemon as resting: `pkg/commands/sessions.go` (about line 172) returns on `claude rm`'s error before it forgets the session.
So a session the CLI has already dropped cannot be demolished from Botropolis at all, from `status --live`, the card or the CLI.

## The fix

When `claude rm` says there is no such job, `rm` goes on to forget the session (the daemon and the ledger), and says the CLI had already dropped it; any other `claude rm` error still stops it.
Tests in `pkg/commands` for both, and L2 re-run against the next release.
