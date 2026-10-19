# 144. A demolished session stays on the map as ruins

**Fixed 2026-10-19 (`705e2b2`, r741). Filed 2026-10-19 (r739), from validating the 0.2.0 release binaries. Nobody's call — a defect, for 0.2.1.**

Depends on: nothing

Step 7 of the [validation checklist](validation-checklist.md): `d d` on a session takes it off the map and out of `claude agents --all`.
On the 0.2.0 binaries, a session started with `c` and then stopped and removed (`botropolis rm`, the same `Sessions.Remove` that `d d` calls) left `claude agents --all` at once, and had no transcript left on disk, but `botropolis status --all` still listed it as **resting** minutes later.
The daemon's ledger (`botropolis/pkg/state/ledger.go`, `sessions.json`, item 86) records every non-empty session it has shown so that a session keeps its lot after *Claude Code* deletes its transcript, and nothing ever removes an entry: `goneSession` (`loader.go`) brings a demolished session back as a gone one, forever.
The dry run against r704 passed only because its session was empty, and the ledger never records an empty one.

## The fix

Demolishing is the user saying the session is gone: `Ledger.Forget(id)`, called when a remove succeeds (the map's `d d`, `botropolis rm`, the TUI's demolish, and `botropolis prune` for what it removes), saved at once; a session Claude Code cleaned up on its own still keeps its lot as item 86 meant.
Its statistics stay, as item 110's prune rules say — check that `rm` and `prune` agree with them.

Tests: a recorded session that is removed → the ledger should not have it, and the next load should not show it; a recorded session whose transcript Claude Code deleted → it should still show as gone (item 86 unchanged); prune → it should forget what it removes.

## Fixed

`705e2b2` (r741), in botropolis.
The daemon keeps the ledger in memory and saves it whole, so a client editing `sessions.json` would have been overwritten at the daemon's next save: forgetting goes to the daemon as a `forget` request, the way packing does, and the daemon rescans so every client drops the session at once.
`d d`, the TUI's demolish, `botropolis rm` and `botropolis prune` each send it after a successful remove, by session id; `rm` given a job id looks up its session in `claude agents --all` first, since a resumed job's id need not start its session's.
With no daemon running, the demolish is noted in `sessions.json.forgotten` beside the ledger and applied when the daemon next loads it, so only the daemon ever writes the ledger (manager, 2026-10-19).
A home the run was pointed at keeps no ledger and forgets nothing.
Statistics already agreed with item 110: prune forgets them and `rm` keeps them, unchanged.
No tombstone for a transcript that outlives `claude rm` (manager, 2026-10-19).

Tests: `TestLedgerForget` (`pkg/state/forget_test.go`) — forgotten, not in the next load or the saved ledger, a session Claude Code cleaned up still gone, notes applied at first load; `TestServeForget` (`pkg/daemon/forget_test.go`) — over the socket, and a demolish noted while no daemon ran is absent from the daemon's first snapshot, which went red with the notes ignored; `TestDemolished` (`pkg/commands/demolish_test.go`) — session id, job id, failed remove, the map, prune and its dry run.
