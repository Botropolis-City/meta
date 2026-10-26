# 252. The second bridge's deck is too low for the liner that passes under it

**Open, in progress since 2026-10-26 in the session "item 252". Filed 2026-10-25 (r1041) at Aria's request, from item 220's frames. Nobody's call — Aria chose the fix.**

Depends on: 220

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
- **The frames** (Aria, 2026-10-26): passed — the deck's underside over the channel at 115 px against the liner's 100 px, at fit and 4x, by day and night; the liner straddling the deck drawn wholly before or behind it at other readings is [item 259](259-a-long-boat-straddling-a-raised-deck-is-drawn-in-one-piece.md). It lands after 0.3.1 is tagged and ships in 0.3.2.
