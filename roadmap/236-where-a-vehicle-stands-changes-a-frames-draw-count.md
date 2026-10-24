# 236. Where a vehicle stands changes how many draw commands a frame takes

**Open. Filed 2026-10-24 (r976), from items 221 and 222 each needing `TestTheWorkAFrameTakes`'s night ceiling raised. Nobody's call — the performance manager measures it first.**

`TestTheWorkAFrameTakes` holds the metropolis's draw commands a frame under ceilings that [item 193](193-a-still-city-is-redrawn-whole-every-frame.md) lowered to what it reached ("today's worst plus 2%"), below a target of 70.
On 2026-10-24 two items moved the night count without drawing anything more:

- [item 221](221-the-railway-is-drawn-over-the-trees.md) draws park trees through a colour matrix, which cannot share a batch with the plain kit sprites beside them: about 2–3 commands (night 39 → 42);
- [item 222](222-cars-drive-on-the-kerb-when-zoomed-in.md) moves where vehicles stand (curved bends, lot lanes, a deeper front lane): one command (night 39 → 40), with the same number of things drawn, because vehicles are drawn in the depth-sorted list among the buildings and one now falls between sprites from different atlas pages and splits a batch.

Both raises were allowed, in the open and under the target, but a count that moves with where a car happens to stand is a ratchet that will creep a command at a time.

**What to find.** Which draws split batches in the depth-sorted pass, by page and by shader, and whether movers can be drawn so their order among buildings does not decide the batching (a mover's sprites on one page, or movers batched by page within a depth band where the sort allows).
Then lower the ceilings back by whatever it saves, and add a case that moving a vehicle within its lane does not change the count.
