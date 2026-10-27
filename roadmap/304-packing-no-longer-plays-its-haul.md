# 304. A packed session's truck drives to the depot at road speed, not in a fixed 2 s

**Done 2026-10-27 (`8d6ce3f`, r1187). Filed 2026-10-27 (r1181), from Aria's use of the 0.3.3 candidate, as a regression; it was not one. Nobody's call — Aria ruled the speed.**

Aria, 2026-10-27: *"noticed that the pack command doesn't play the animation anymore. Where did that go?"*

Packing (item 86, slice 3) draws a haul: a truck carrying the session's crate from its lot to the depot over `PackFor` (2 s), or back on unpacking, a cross-fade under reduced motion (`pkg/city/haul.go`).
`Scene.noteHauls` starts one when a session's spot differs between two snapshots: it compares where each building stood (`b.Rect.Center()`, `b.Packed`) across `s.city.Buildings()`.

## It still played

Nothing since v0.3.2 lost the haul.
At HEAD (`9b262e6`), on scratch homes, it starts and is drawn:
in the scene's own test;
in the Drive, from Shift+P and from the card's *pack* with the card pinned;
end to end through a real daemon with a ledger, `commands.Feed` and the proto client `liveActor.pack` uses;
in `--check-frames` under Xvfb, where the standing and straight frames agree and the truck is in the frame;
for every one of the metropolis scenario's 28 sessions;
and in the real v0.3.2 and HEAD binaries side by side on Xvfb, where both show the truck about 0.3 s after the pack.

Aria, 2026-10-27, once asked: *"It's just really really fast, so you barely can see it if you're watching for it."*
In 2 s a truck crosses a large city to the depot faster than anything else on its roads, and the camera's refit as the depot appears takes the eye with it.

## The fix

Aria's ruling, 2026-10-27: the haul drives at the speed of the city's other trucks, `TruckSpeed`, as deliveries and messages do, so a far depot takes longer.
It takes at least 2 s and at most about 6 s.
Reduced motion keeps its 300 ms cross-fade.

## Closed

A packed or unpacked session's truck now takes its distance at road speed, 3 cells a second as deliveries do, between 2 s and 6 s, set when the haul starts; reduced motion keeps the 300 ms cross-fade. Nothing since v0.3.2 had lost the haul: it was there, only too quick across a big island to follow. `TestHaulFor` and the extended `TestHauls` hold it, red first with a fixed span; landed as `8d6ce3f` (r1187), with a Changed entry.
