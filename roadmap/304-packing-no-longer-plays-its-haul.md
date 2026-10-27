# 304. Packing a session no longer plays the truck carrying its crate to the depot

**Open, in progress since 2026-10-27 in the session "item 304". Filed 2026-10-27 (r1181), from Aria's use of the 0.3.3 candidate. Nobody's call — a regression.**

Aria, 2026-10-27: *"noticed that the pack command doesn't play the animation anymore. Where did that go?"*

Packing (item 86, slice 3) draws a haul: a truck carrying the session's crate from its lot to the depot over `PackFor` (2 s), or back on unpacking, a cross-fade under reduced motion (`pkg/city/haul.go`).
`Scene.noteHauls` starts one when a session's spot differs between two snapshots: it compares where each building stood (`b.Rect.Center()`, `b.Packed`) across `s.city.Buildings()`.

## Suspects, to bisect first

Since 0.3.2, changes that touch exactly that path or what draws it:
- item 270's slice 2 or 7: `City.Buildings()` computed once per build, a district index, culling;
- item 274 and 273's shared `Shown` filter in `Scene.restate`, which every snapshot passes before `build()`;
- item 278: packing from the card now acts (`Scene.Act`), perhaps not through the path `TogglePack` takes;
- item 212's still key and held frames: a haul's truck is a mover, and the still city held as one block must not hide it.

## The fix

Find which, from the 0.3.2 tag forward, with a test that fails today: when a session is packed between two snapshots, a haul starts, its truck is drawn on the frames during `PackFor`, and it arrives at the depot; the same for unpacking; from both Shift+P and the card's *pack*.
