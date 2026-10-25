# 212. Every frame records every drawable again, only to find most of them unchanged

**Open, in progress since 2026-10-25 in the session "item 212". Filed 2026-10-23 (r953), from item 161. Nobody's call — the budget is set (a visible city ≤ 10% of a core).**

Depends on: nothing

[Item 193](193-a-still-city-is-redrawn-whole-every-frame.md) composes the standing city once and replays only what moves, deciding what changed by hashing each drawable's recorded draws. But to hash them it **records every drawable every frame**: `note` is 43% of Draw at fit and 59% at full zoom on the real history (r935, [item 161](161-drawing-a-frame-costs-41-ms-of-cpu.md)'s profile), tessellating and hashing each building, line and label only to find its record unchanged and blit the standing layer. A focused city on the real history still uses about 60% of a core against 10%, and item 161 sees no other change that can close most of that gap.

## The fix

A still drawable whose inputs have not changed reuses last frame's record instead of being drawn again: a key per drawable kind (a building's session state, zoom phase, tint, …), as [item 192](192-a-building-is-drawn-from-many-pieces-every-frame.md)'s look keys do. The risk is the one item 192 and [item 207](207-an-unfocused-city-redraws-the-whole-world-per-change.md) met: a key that misses an input leaves the city stale. So the guard comes first:

- a randomised check, as item 207's: seeded walks of snapshots, pointer, view and camera moves, asserting after every step that the frame drawn with reused records equals one drawn with every record made afresh;
- the from-scratch path stays as the oracle, and the frame check compares against it.

Write the design (the keys per kind, and how each is derived from what the drawable reads rather than listed by hand) and send it before any code.

Tests: as above, plus the real-history focused CPU at fit and full zoom through the benchmark session, against 10%.

## Answered while building

- **Who approves the design** (Aria, 2026-10-25, asked by the manager): she does. The session researches and writes the per-drawable keys design and sends it to the manager, which brings it to Aria; no code lands until she approves it.
