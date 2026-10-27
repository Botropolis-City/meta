# 278. Packing a session leaves it standing, boarded up, instead of taking it to the depot

**Fixed 2026-10-26 (`71bef08`, r1130). Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — a defect; Aria ruled packing keeps its meaning.**

Depends on: nothing
Landed: slice 1 (`71bef08`, r1130).

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

## Answered while building

- **The cause and the fix** (session's diagnosis, approved by the manager, 2026-10-26): the card's *pack* and *unpack* buttons did nothing, because `Scene.Act` had no case for them and fell through to an empty action, which leaves a shuttered building looking *just boarded up*; Shift+P worked throughout. A live session packed comes back as soon as it works, as designed, and packing one now says so. A guard holds that every action every card offers either asks for something or says what happened.

## What it was

The card's *pack* and *unpack* buttons did nothing.
`Scene.Act` had no case for either, so pressing one asked the actor for nothing and said nothing, and a shuttered building stayed boarded up where it stood.
Shift+P went another way, through `TogglePack`, and worked: driven in the real city against a private daemon on the real home, a shuttered session and a resting one each went to the depot as a crate and stayed there across later snapshots.
The daemon, the ledger, the deltas and the depot were all sound.

A live session packed comes back within seconds, as `unpackOnWork` intends: this item's own session, packed at 22:31:26, was back on its lot by 22:31:31.
The manager ruled pack stays offered on a live session, because one waiting on you is live but quiet, and the footer now says *"packed <title>; it comes back when it works again"*.

## What landed

`Act` handles pack and unpack, Shift+P goes through `Act` too, and the footer says what happened.
`TestCardActionsDoSomething` presses every action each card state offers (working, needs you, resting, shuttered, overgrown, packed) and fails on any that asks for nothing, says nothing and changes nothing; only pack and unpack failed it.
The Drive harness gained a `button:<label>` target, and `TestPackFromTheCity` clicks the card's *pack* and presses Shift+P through the city's own input.
`TestServePack` holds a packed session through a second rescan, and brings back one that works after packing; the second was checked by mutating `unpackOnWork`.
