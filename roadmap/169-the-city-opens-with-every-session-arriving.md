# 169. The city opens with every live session arriving by tug, so for its first seven seconds they are bare lots

**Fixed 2026-10-20 (`e164a0d`, r812). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect, for the next patch release (the manager, 2026-10-20).**

Depends on: nothing

`noteVoyages` (`botropolis/pkg/city/voyages.go`) promises that *"the first snapshot only takes note, so the city does not open with a fleet"*.
It does open with one.
Every session that is live when the city starts is treated as new: a tug sails it in for `SailFor` (6 s), its lot stays bare while it sails, then it is built over `BuildFor` (1.8 s), with fence, scaffolding and crane.

![The hamlet at 0.5 s, 3.5 s, 6.5 s and 10 s after it opened](../docs/references/169-the-city-opens-with-a-fleet.png)

`hamlet`, 13:00, a ten-second clip at two frames a second through `make demo-media`: at 0.5 s and 3.5 s the working and waiting sessions are dark empty lots with a tug on the river, at 6.5 s they are building sites, and by 10 s their buildings stand.

## Why

`first := s.known == nil` decides whether a snapshot is the first.
But `SetSnapshot` runs before any snapshot has arrived: `(*Game).setStatsOn` calls `Scene.SetLedger` at start-up whenever statistics are on, which is the default, and `SetLedger` rebuilds with `s.SetSnapshot(s.snapshot)` — the scene's empty zero snapshot.
That pass sets `s.known` to an empty, non-nil map, so the real first snapshot is the second, and every session in it is an arrival.
`SetLadder` does the same when the configured thresholds differ from the scene's.
`noteDrones` uses the same `s.known == nil` test, so subagents already at work at start-up take off instead of being found on station.

## What it costs

- Every still the demo films shows the live sessions as empty lots: the website's frames, `layers/pressure.png`, `workshop/needs-you.png` — whose selected session, the subject of the shot, has no building — and the audit's own.
- Every opening of the city spends its first seven seconds sailing and building what was already there, which is the motion the map reserves for something actually happening.
- At night the glow of those sessions is drawn over the empty lots, which may be part of what item 74 sees.

## The fix

Decide "first" by whether a real snapshot has been seen — a flag set by the first `SetSnapshot` that does not come from the scene itself, or `known` left nil until the snapshot carries any session or a time — rather than by `known` being nil.
A test in `pkg/city`: a scene given a ledger, then a snapshot with live sessions, launches no voyages and no drones.

## Closed

Fixed in `e164a0d` (r812).
The scene now records whether a snapshot has come from outside it, `opened`, set only by the public `SetSnapshot`.
Its own rebuilds — `SetLedger`, `SetLadder`, `SetTyping`, `Unhide`, hiding a project, changing a district's type, dropping a dragged district, and the veil — go through a private `restate()`, which never sets it.
Every pass that only takes note of the first snapshot reads that flag instead of whether its own map is nil.

The fault was wider than voyages and drones.
The same start-up also hoisted every open pull request's flag, celebrated every merged one and sent a van for every message already between projects; compactions and tool-call loads were spared only because they skip a session they have not seen before.
`TestTheCityOpensOnWhatIsAlreadyThere` in `botropolis/pkg/city/opening_test.go` covers each setting that can run first, with a control and a guard that a session arriving afterwards still sails in; it was red for every setting before the fix.

Rebasing onto item 168 turned up a related defect in its veil: those same internal rebuilds re-applied the veiled snapshot through `SetSnapshot`, which kept it as the real one, so a ledger change or a hide while sharing left the veil on after it was lifted.
`restate()` rebuilds from the real snapshot through the veil, and a case in `TestVeil` covers it; item 168's session agreed.

The frame is `botropolis/docs/screenshots/r811-item-169-opening-after.png`, `hamlet` at 13:00 at the same four moments as the reference above: both live sessions stand from the first frame, with no tug and no build site.
Aria approved it, 2026-10-20.
Its name says r811 because another landing went in ahead of it while it waited for the landing lock; the fix is r812.
