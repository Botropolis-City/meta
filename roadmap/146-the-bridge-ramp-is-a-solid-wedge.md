# 146. The bridge's ramp is a steep solid wedge

**Fixed 2026-10-19 (`de16c0a`, r750). Filed 2026-10-19 (r748) at Aria's request, from item 132's frames. Nobody's call.**

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

## Decided (2026-10-19)

The session measured the layout first: the landing is the T on the west ring road, with a block inland of it, and the rail's west leg was the very next cell, so the ramp could only grow seaward and the rail was in the way.
The manager chose to move the freight loop's west leg out one cell, to the plan's edge, two cells off the west road as the north leg already stands off the north road; widening the belt for every plan was set aside as a larger change.

## Closed (2026-10-19)

Slice 1 (`de16c0a`, r750) built it.
The road ramps from the landing's centre, the T, over a cell and a half to the first span, drawn as half-cell pieces of sloped deck, each on a pier at its high end, with girders and railings, open underneath, in the deck road's own colour with its lane line.
`City.Bridge` carries the ramp's cells and its run, and `Rise` climbs over it.
The slope is 0.42 rise over run, where the wedge was 1.26, measured with the deck's height turned back into world units through the 2:1 view; `TestBridgeRamp` bounds it at 0.8 at every atlas and heading, and fails on a ramp cut into pieces longer than half a cell.
Item 132's crossing, clearance and draw-order tests still hold, a truck halfway up the ramp draws over it, and nothing is planted or laid as street on it.
Item 85's plan test now puts the loop's west corners in column 0, and the trains-fit and river-clear tests pass on the longer loop.

Slice 2 (`9c72892`, r751) is the frames, `botropolis/docs/screenshots/r750-item-146-ramp-h0.png`, `-h90`, `-h180` and `-h270`, staged as item 132's were by a hook that was not committed.
The changelog says it in `df1480c`.

For Aria: in h0 and h270, a train piece standing just beyond the deck's far side draws over its railing, as it did in item 132's r707 frame; under the deck the order is right.
It is not this item's, and would be a separate one.

**Aria's verdict** (2026-10-19): the four r750 frames are approved.
