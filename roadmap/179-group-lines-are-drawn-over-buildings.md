# 179. Group lines are drawn over the buildings they pass behind

**Closed 2026-10-20 by adjudication: Aria ruled "Drop it", and the lines stay drawn over the city. Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154, from its matters of taste, at Aria's request.**

Depends on: nothing

A group's line runs across its districts as a dashed or solid stroke, and it is drawn after everything on the ground, so it crosses the front of any building in its way.
At closest zoom on the `layers` demo city, turned three times, a line runs down the library's facade from its roof, over the plaza and across the road.

![A group line over the library](../docs/references/179-group-lines-are-drawn-over-buildings.png)

Shot: `layers`, keys `R R R` and ten `Equal`, 13:00, 1920×1080; the crop is (0, 300)–(700, 1080).

`drawIso` (`botropolis/pkg/render/iso.go`) draws every layered item, then the night overlay and its lights, and only then `groupLines`, for the faded lines and again for the lit stations.
So a line is on top of every building and, at night, brighter than the overlay that darkens them.
Item 87 drew the lines as a transit map laid over the city, which may be why; but a line that cuts across a building's front reads as a wire strung through it, and it hides the windows and signs it crosses.

What it wants decided while fixing: whether the line goes into the depth sort as something on the ground, so buildings in front hide it, or stays on top and gives way where it crosses a building (a gap, or a fade under the footprint).
A test can hold a line's segment behind a building's footprint to being drawn before the building.

## Closed: dropped

**Aria, 2026-10-20: "Drop it."**
The lines stay as they were before this item, drawn after the scene and over every building, and nothing landed in botropolis.
Do not re-file this as a defect: drawing the line on the ground was built, tested and filmed, and ruled out on the frames.

**Why.** Across the whole city, a line broken into stretches wherever it passes behind a building reads worse than a line drawn over it.
In the item's close-up the library came out clear, but on the metropolis, fitted and one notch in, at 13:00 and 23:00, every long line was cut into pieces by the lots in front of it, and she judged the overview, not the close-up.

**What was tried**, so the next attempt starts from it rather than from nothing.
Each segment was cut into tile-long pieces in the depth sort, a level below what stands on the ground, so a building in front of a piece or over it hid it; stations and site offices stayed on top, because a station stands inside its own buildings' footprint and is what is hovered and clicked.
Leaving the line on top and opening a gap under each footprint was rejected first, because it needs every sprite's silhouette as a mask.

**At night**, a line in the depth sort is darkened by the wash, and that fails the day line's own contrast.
Contrast is WCAG's ratio, from the better of the line's ink and its casing against the ground beside it, sampled from the item's shot at r819:

| ground | day | night, under the wash | night, with the lit windows |
| --- | --- | --- | --- |
| plaza | `#b3b3b6`: 7.8 | `#686976`: 3.3 | 4.3 |
| road | `#767d96`: 4.0 | `#464b64`: 2.4 | 6.9 |
| grass | `#829c6e`: 5.4 | `#1c232b`: 4.4 | 12.7 |

The bar was the day line's worst, 4.0:1 on the road.
No colour under the wash can meet it: white comes out at `#93949f`, 2.85 on the night road.
So the pieces were laid at night with the lit windows (item 166's layer), which keeps their day colours and lets every sprite drawn after them cut them out.

**Cost**, by count, from `BenchmarkDrawANightFrame` on the fitted metropolis: 405 line pieces a frame, taking the depth sort from 358 drawables to 763, and the night's cuts from 97 to 129.
Drawn on top, as they stay, the lines add nothing to the sort.
