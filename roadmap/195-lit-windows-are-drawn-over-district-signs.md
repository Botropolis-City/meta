# 195. Lit windows are drawn over district signs at night

**Fixed 2026-10-21 (`76cfde9`, r853). Filed 2026-10-21 (r852) by Aria, from item 191's night frames. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`76cfde9`, r853).

In `botropolis/docs/screenshots/r851-item-191-night-3x.png` (both halves, so it predates item 191), the tower behind the "orchard / your move" district sign shows its lit windows straight through the sign: yellow panes run across the sign's board and its words.
Aria, 2026-10-21: *"the window lights are drawn over the label. The label should be in front."*

The lit windows come from [item 166](166-lit-windows-are-round-halos-not-windows.md)'s lights layer, which is laid over the scene after it is drawn, and a sprite drawn later in the depth sort cuts its shape out of that layer. The sign is drawn in front of the tower but does not cut the layer — so it is either drawn outside the depth sort the cuts are taken from, or as a label after it. Find which, and check every other thing drawn over buildings the same way: station plates, badges, map labels, the hover card, the move tones, the group stations kept on top by item 179.

## The fix

Everything that should sit in front of a lit building either cuts its shape from the lights layer or is drawn after the layer is composited. Labels and signs should be after it, since they are not part of the scene's depth.

Tests: `--check-lights` gains a lit tower with a district sign in front: no lit pixel inside the sign's board. The same for a station label and a badge over a lit building. A night frame for Aria at the same crop.

## Diagnosis

Only sprites cut the lights layer: `punch` is called from the sprite draws, and the sign was painted, so it never cut.
The district sign is in the depth sort, as item 88 placed it, and its board was a plain `vector.FillRect`, which goes around `pkg/shapes`' painter.
The audit found the same fault in everything painted in the depth sort.
A building's own painted name, beacon, flags and smoke are painted after its own windows are noted.
So are a scaffold's tubes, boards and ladder, a monument's paint, a spire, bridge decks and fountain rings.
Station plates, badges, map labels, group lines and stations (item 179), the tower plate and the hover card are drawn after the layer is laid, so they were already in front.

## The decision

The fix is at the painter, not per offender (the manager, for Aria, 2026-10-21).
Every shape the painter draws while the lights are noted, and every painted word, cuts the lights at its own alpha.
A half-transparent shape dims the light behind it rather than putting it out, and a glow is light, so it does not cut.
The sign stays in the depth sort and cuts, rather than moving after the layer.
It has stood in the depth order since item 88, so a building in front of a sign still hides it.
The item's other option, drawing it after the layer, would paint it over buildings that stand in front of it.
Cuts may not push item 194's frame counts past their ceilings: a failure to fix, not a ceiling to raise.

## Fixed

**What is painted in front of a lit window cuts it** (`76cfde9`, r853).
The painter tells the lights of every shape it draws, and `g.sign` of every word, and each cuts the lights laid behind it in depth order, at its own alpha.
Render's hard-edged rectangles and lines moved onto the painter too, and `TestNothingIsDrawnAroundThePainter` fails on any vector call in render but the night wash.
`g.paintUncut` turns cutting off for painting somewhere other than the screen, which item 192's cached looks use.

**Tests**, each mutated red: the painter reports each kind of shape and not a glow, and render notes a cut only over a lit pane.
`--check-lights` draws a lit tower behind a district sign, its own painted name, painted shapes, a hard-edged box and a half-transparent shape, and under a station label and a badge.
It fails where more light shows than the thing in front leaves uncovered, and where the half-transparent shape leaves other than half.
Every case in the depth sort went red with cutting switched off; the two labels do not, because they are drawn after the lights, and they pass drawn before them too, since their boxes now cut.

**Cost**, on item 194's metropolis demo at night: 317 commands and 79,884 indices a frame, against 329 and 78,612 before and ceilings of 341 and 80,200; by day, 268 commands, from 277.

**Frame**, approved by Aria on 2026-10-21: `botropolis/docs/screenshots/r853-item-195-night-3x.png` (landed at r854), the crop of r851's, main on the left.

**Known limit**: a sprite fading in or out by its tint, such as a building arriving on a truck, still cuts the light behind it at full strength while it fades.
That predates this item.
