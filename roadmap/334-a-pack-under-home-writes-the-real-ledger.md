# 334. Packing a session under `--home` writes the real daemon's ledger

**Fixed 2026-11-03 (`505fba5`, r1239). Filed 2026-11-03 (r1234), found by item 333's session. Nobody's call — a defect.**

Landed: slice 1 (`2239143`, r1235).
Landed: slice 2 (`505fba5`, r1239).

A city started with `--home` (a staged home, as the demo and the tests use) sends a pack to the default socket's daemon, which keeps the real ledger, so packing a staged session marks a real one, or a ghost, in the user's own depot.
`--home` was meant to write nothing of the user's (item 333's details say so for the walk, and the sweep refuses there), and a single pack slipped past that.

## The fix

A city under `--home` talks only to a daemon for that home (its own socket, as the acceptance tests start one), or refuses the action with its reason when there is none; never the default socket.
A test: a pack under `--home` with no daemon of its own is refused and the default daemon's ledger is untouched.

## Closed

The hole was wider than the pack.
Under `--home` without `--socket`, `cfg.Socket` is the default socket, and the city used it for every daemon call.
So such a city also showed the real daemon's sessions (which is how a staged pack could reach a ghost), searched through it, read its loading meter, and its settings' Restart restarted the real daemon.
Demolish also asked the real daemon to forget.

`ownSocket` in `pkg/app` now gives no socket to a run under `--home` without `--socket`, the rule `status` and `bar` already used.
Slice 1 (`2239143`) refuses pack and close-up there, saying to pass `--socket`, and notes a demolish only in the private state.
Slice 2 (`505fba5`) moves the feed, the loading meter, the search and the restart onto it: the reads fall back to the home, and restart refuses.
Tested in `pkg/app/home_socket_test.go` against a fake daemon at the default socket path: under `--home` without `--socket`, nothing reaches it; with `--socket`, each reaches the home's own socket.
The restart test passes in a fake `daemonctl.System`, because a red run of it through the real one sent SIGTERM to the process holding the fake socket, which was the test itself.

Left open, read-only, for the manager to file: `events`, `find`, `bar`'s live feed, `notify` and the TUI still read the default daemon under `--home` without `--socket`.
