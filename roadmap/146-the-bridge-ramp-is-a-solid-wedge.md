# 146. The bridge's ramp is a steep solid wedge

**Open, in progress since 2026-10-19 in the session "item 146". Filed 2026-10-19 (r748) at Aria's request, from item 132's frames. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`de16c0a`, r750).
Landed: slice 2 (`9c72892`, r751).

[Item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md) carried the bridge road over the rail on a raised deck, climbing from an abutment on the landing cell's outer half, so the ramp is a steep solid wedge (`botropolis/docs/screenshots/r707-item-132-bridge-h0.png`).
Aria, 2026-10-19, reviewing those frames: **a gentler ramp** — longer and lighter, open underneath like a span, not a solid wedge.

## The fix

Lengthen the climb so it reads as a ramp rather than a block: start it further back along the avenue (the T junction may sit on the ramp's foot, or the ramp may begin on the cell before the landing, whichever the layout allows), and draw it as a sloped deck on short piers with its side faces open underneath, matching the deck over the water.
Art follows `botropolis/design/art-sources.md`: geometry built in code or the pack's pieces.
Keep item 132's guarantees: the rail passes under the first span with clearance, trucks ride the deck, and no street, tree or fixture sits under or on the ramp.

Tests: item 132's crossing, clearance and draw-order tests still hold; the ramp's slope is under a bound (rise over run) instead of the landing's half cell; nothing is planted under it. Frames at four headings, as item 132's.
