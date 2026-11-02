# 334. Packing a session under `--home` writes the real daemon's ledger

**Open, in progress since 2026-11-03 in the session "item 334". Filed 2026-11-03 (r1234), found by item 333's session. Nobody's call — a defect.**

Landed: slice 1 (`2239143`, r1235).

A city started with `--home` (a staged home, as the demo and the tests use) sends a pack to the default socket's daemon, which keeps the real ledger, so packing a staged session marks a real one, or a ghost, in the user's own depot.
`--home` was meant to write nothing of the user's (item 333's details say so for the walk, and the sweep refuses there), and a single pack slipped past that.

## The fix

A city under `--home` talks only to a daemon for that home (its own socket, as the acceptance tests start one), or refuses the action with its reason when there is none; never the default socket.
A test: a pack under `--home` with no daemon of its own is refused and the default daemon's ledger is untouched.
