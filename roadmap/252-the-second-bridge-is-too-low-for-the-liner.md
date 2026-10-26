# 252. The second bridge's deck is too low for the liner that passes under it

**Done 2026-10-26 (`c990b7d`, r1070). Filed 2026-10-25 (r1041) at Aria's request, from item 220's frames. Nobody's call — Aria chose the fix.**

Depends on: 220
Landed: slice 1 (`c990b7d`, r1070).

[Item 220](220-a-large-island-gets-a-second-bridge.md)'s second bridge crosses the river on a raised deck, and boats pass under it: the deck draws over a boat's stern correctly, but the weekly-usage liner's superstructure and funnels stand well above the deck, so a ship that size could not fit under it.
Item 220's crops at 4x show it (`liner-58-zoom.png` and `liner-61-zoom.png`, filmed in that item's worktree with weekly usage staged at 58% and 61%).

Aria, 2026-10-25, choosing between raising the deck, keeping the liner out of the bridge's row, and leaving it: *"Raise the deck"*.

## The fix

Raise the second bridge's deck over the river channel high enough to clear the tallest boat drawn (the liner, at its largest), with longer ramps up from each bank so the climb stays as gentle as the first bridge's; the piers lengthen with it.
The deck's height comes from the boats' own drawn heights, not a number tuned by eye, so a taller boat raises it or fails a test.
The first bridge crosses no river and stays as it is.

Tests: the deck's underside over the channel is above the tallest boat's drawn top, at every heading; the ramps climb no more steeply than the first bridge's; trucks still ride the deck and boats still pass under it in draw order; frames of the liner under the deck at fit and at 4x, by day and night, for Aria.

## Answered while building

- **The shape** (manager, 2026-10-26, from the fix above): a hump, at channel height over the river band the boats sail in (not the banks' wander), climbing over rail and belt and coming back down to deck height as far past the band as it climbed, so the far end, the haze and the fog are unchanged. Channel height is the tallest boat's per-column drawn top (the liner, 100 px at zoom 1 against the deck's 56) plus the first bridge's 15% headroom and the girder, measured off the sprites once per page; the climb is about 0.30 against the first bridge's 0.42. `Bridge.Rise` becomes `Bridge.Lift`, item 146's cases kept.
- **The frames** (Aria, 2026-10-26): passed — the deck's underside over the channel at 115 px against the liner's 100 px, at fit and 4x, by day and night; the liner straddling the deck drawn wholly before or behind it at other readings is [item 259](259-a-long-boat-straddling-a-raised-deck-is-drawn-in-one-piece.md). It landed just after 0.3.1's version commit, in time for 0.3.1 (Aria, 2026-10-26).

## Closed

Done by slice 1, two commits in botropolis: `c990b7d` (r1070), the work, and `0959e75` (r1071), its line in the `[0.3.1]` changelog's second-bridge entry.
`City.Bridge` gains a `Channel` (the river band) and a `Profile` of knots at the ground, deck and channel heights, and `Lift(p, heights)` replaces `Rise`; the renderer says how high each height is at its camera, the channel's from `drawnTop`, measured off each boat sprite as its page is put up.
Bridge parts carry distances along the bridge, and a deck cell the road climbs or comes down over is cut into half-cell segments on piers, as the ramp is.

Tests: `TestBridgeProfile` in `botropolis/pkg/city/bridgeprofile_test.go` (the first bridge's one ramp in a small and a large city, item 146's cases; the second's channel, its climb to deck height by the rail, channel height across the band, the descent as long as the climb and before the haze, and a truck at channel height over every river cell); `TestDrawnTop` and `TestSecondBridgeClearsTheBoats` in `botropolis/pkg/render/channel_test.go` (the measure on a drawn box and a box with a post, and at every atlas and heading the underside over the channel above the tallest boat, the underside over the rail above the trains, and no change of height steeper than the first bridge's ramp); `TestBridgeRamp` over all three bridges; and a truck over the channel riding at its height and drawn over the deck in `TestEveryBridgeIsDrawn`.
Each was red before the code it holds, and the channel height, the measure, the cutting, the truck's lift and the descent were each mutated red.
The night frame-work test held at 37.

**Deviation, flagged for Aria:** the test tree checked the measure against `roofLift` on a kit building, but kit buildings carry rooftop fittings that only the column measure sees (building-a reads 116 against `roofLift`'s 104), so the check is made on a box drawn in the test, plain and with a post.

**Frames**, git-ignored in the item 252 worktree at `botropolis/dist/item-252/frames/`: `day-fit.png`, `night-fit.png`, `day-4x.png` and `night-4x.png`, a 17-district city at 2400×1350 with weekly usage at 61%, and `day-55-4x.png` and `day-64-4x.png`, which show item 259.
