# 144. A demolished session stays on the map as ruins

**Open, in progress since 2026-10-19 in the session "item 144". Filed 2026-10-19 (r739), from validating the 0.2.0 release binaries. Nobody's call — a defect, for 0.2.1.**

Depends on: nothing

Step 7 of the [validation checklist](validation-checklist.md): `d d` on a session takes it off the map and out of `claude agents --all`.
On the 0.2.0 binaries, a session started with `c` and then stopped and removed (`botropolis rm`, the same `Sessions.Remove` that `d d` calls) left `claude agents --all` at once, and had no transcript left on disk, but `botropolis status --all` still listed it as **resting** minutes later.
The daemon's ledger (`botropolis/pkg/state/ledger.go`, `sessions.json`, item 86) records every non-empty session it has shown so that a session keeps its lot after *Claude Code* deletes its transcript, and nothing ever removes an entry: `goneSession` (`loader.go`) brings a demolished session back as a gone one, forever.
The dry run against r704 passed only because its session was empty, and the ledger never records an empty one.

## The fix

Demolishing is the user saying the session is gone: `Ledger.Forget(id)`, called when a remove succeeds (the map's `d d`, `botropolis rm`, the TUI's demolish, and `botropolis prune` for what it removes), saved at once; a session Claude Code cleaned up on its own still keeps its lot as item 86 meant.
Its statistics stay, as item 110's prune rules say — check that `rm` and `prune` agree with them.

Tests: a recorded session that is removed → the ledger should not have it, and the next load should not show it; a recorded session whose transcript Claude Code deleted → it should still show as gone (item 86 unchanged); prune → it should forget what it removes.
