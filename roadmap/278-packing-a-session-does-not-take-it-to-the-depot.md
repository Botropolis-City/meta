# 278. Packing a session leaves it standing, boarded up, instead of taking it to the depot

**Open. Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — a defect; Aria ruled packing keeps its meaning.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: *"Manually packing a session, just makes it boarded up. It doesn't actually pack it up. Is that not how we get sessions to disappear manually?"*
Asked, she ruled it a defect to investigate: packing still means *off the district and into the depot*, and unpacking brings it back.

## How it is meant to work

Shift+P, or *pack* on the card, calls `TogglePack` (`pkg/render/keys.go`, `pkg/city/scene.go`); the daemon's `OpPack` has `Loader.Pack` write `PackedAt` to the ledger (`pkg/state/loader.go`, `ledger.go`), the session's rung becomes `RungPacked` (`pkg/state/ladder.go`), and `pkg/city/city.go` moves it into the depot's crates on the south edge (`pkg/city/depot.go`).
*Boarded up* is another state, the *shuttered* rung of a resting session idle seven days.

## Suspects, to reproduce first

- `unpackOnWork` (`pkg/state/loader.go`) unpacks any packed session whose `LastActivity` is after `PackedAt`; a live session packed keeps working and unpacks at once, and anything touching a resting session's transcript after packing does the same.
- The pack may reach the daemon but the building may stay drawn as before, if the snapshot that carries it is held or the city keeps a kept record of the building (item 212's records), drawn boarded because it was shuttered.

## The fix

Reproduce packing a shuttered session, a resting one and a live one, from the key and from the card, and find which path leaves it standing; fix that, with a test per path that holds the session in the depot after the next snapshot.
If a live session must unpack on work, say so on the card when it is packed, rather than appear to do nothing.
