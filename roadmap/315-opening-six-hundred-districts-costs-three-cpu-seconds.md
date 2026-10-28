# 315. Opening the six-hundred-district city costs about three CPU-seconds, against a budget of one

**Fixed 2026-10-28 (`9b5e96f`, r1206). Filed 2026-10-28 (r1197), from item 311's CPU bar.**

Depends on: nothing
Landed: slice 1 (`035a9dd`, r1202).
Landed: slice 2 (`55ef60e`, r1203).
Landed: slice 3 (`241f12d`, r1204).
Landed: slice 4 (`9b5e96f`, r1206).

The performance manager set the city's own CPU from start to its first frame on the 600-district fixture at no more than 1 CPU-second, `--record` included.
After item 311's fix (`1259a1e`, r1197) a recording city spends 2.7–3.3 CPU-s, and a plain headless city 2.55, so it is the opening's cost, not recording's.
Item 311's profile names two parts:

1. **The collector spirals at the city's 300 MiB `GOMEMLIMIT`:** the live heap is 267–399 MB around the first frame, and about 250 collections run in under a second, about 1.3 CPU-s.
   A live heap above the limit cannot be collected below it, so the limit makes the collector run flat out.
2. **About 1.4 CPU-s in llvmpipe during the opening**, probably the atlas upload.

## The fix

Bring the opening under the budget: a live heap at the first frame that the limit can hold, or a limit the stress city's peak bar allows (1 GiB) without spiralling, which is Aria's call if it changes the 300 MiB she set; and an opening that uploads only what the first frame draws.
Item 311's test, `it should spend at most 1 CPU-second before its first frame`, held unlanded in its worktree, lands with this item, red first.
The budget is the target: if it cannot be met, bring the evidence to Aria; do not loosen it.

## Answered while building

- **What held the heap over the limit** (item 315, 2026-10-28): not the city but dead buffers.
  Each recorded mesh kept slices of the draw list's vertex and index buffers, so every growth of a buffer left the commands before it holding the old one: 381 MiB live after the first frame, 330 of it mesh buffers.
  Slice 1 moves the meshes onto a grown buffer; the 300 MiB limit is unchanged.
- **The heap's bar?** At most 150 MiB live on each of the first three frames, half the limit, so the collector's own goal stays under it (manager, 2026-10-28).
  It read 123/145/147 MiB in the worktree and 121/140/142 in the quiet suite at r1204: 3 to 8 MiB of margin, so a later slice that eats it is the finding.
- **What llvmpipe spent in the opening?** Not the atlas: Go was idle then, the pages already up.
  It was the opening panel itself, paced to ten draws a second, about 1.2–1.7 CPU-s; slice 2 stops a headless city drawing a panel nobody sees (manager, 2026-10-28).
- **Fewer llvmpipe threads for the headless child?** Not now: it tunes the renderer the bar is measured on and costs later frames' wall time (manager, 2026-10-28).
- **Item 311's test** lands only once it passes, not red, so a red performance tier does not hide the next regression (roadmap manager, 2026-10-28).
- **The opening's bar, once the evidence was in?** Aria, 2026-10-28: "2.5 CPU-s", headless, from start to first frame.
  The 1 CPU-second estimate left out that a first frame bakes every look cold; the performance manager changes `performance/budgets.md`, and item 311's test holds 2.5.
- **No cracks below a quarter zoom?** Aria, 2026-10-28: "Yes, take S4".
  Below a quarter zoom a tile is under 4 pixels and a crack a speck; slice 4 strokes none there, on lots and district floors.

## Where it stands after slice 3

Measured 2026-10-28 at r1204, in one locked run on the reference machine: the city's own CPU from start to its first frame on the 600-district fixture.

| run | CPU-s |
| --- | --- |
| headless recording, which the bar measures | 1.63, 1.86, 2.09 (3.1–4.0 at r1197) |
| windowed recording on the machine's own GPU, opening panel drawn | 1.47 |
| headless, no cracks stroked where a tile is under 4 px | 1.46, 1.51 |

No one part is left to remove: the first frame's draw in Go about 0.5, its draw calls into llvmpipe about 0.35 and llvmpipe's rasterising threads about 0.45, the collector 0.27, the atlas pages 0.23, the scene build 0.12.
The budget's own reasoning put one fitted frame at 0.3–0.5; headless, it costs about 0.9–1.3.
Leaving out the cracks where a tile is under 4 px saves 0.3–0.4 and changes 1.58% of the first frame's pixels, by at most 35 levels, as a speckle across the district floors.
The evidence and these options went to Aria through the roadmap manager on 2026-10-28: that picture change, leaving the opening over the bar for now, or judging the bar on a real GPU, which is a change of definition and alone does not pass either.
Item 311's test waits, unlanded, for whatever meets the bar.

## Closed

Four slices, and item 311's test at Aria's bar:

1. A grown mesh buffer leaves no old one held: the first frames hold 86–91 MiB of live heap, from 381, and the collector no longer spirals at the 300 MiB limit, which is unchanged (`035a9dd`, r1202).
2. A headless city draws no opening panel nobody sees (`55ef60e`, r1203).
3. A street walk takes its cheapest step off a heap, the same roads at a fraction of the cost (`241f12d`, r1204).
4. Below a quarter zoom no crack is stroked (`9b5e96f`, r1206).

`TestARecordingCityOfSixHundredDistrictsOpening` holds the opening to 2.5 CPU-seconds headless (`9f2c5d0`, r1207); under the lock it read 2.35 against it, and scratch runs of the same build 1.46–1.67, so its margin is thinner than those suggest.
`TestACityOfSixHundredDistrictsFrames` holds the heap at 150 MiB on each of the first three frames; the fitted frame read 14.0 ms against 16.
**Deviation, flagged for Aria:** the bar the item set, 1 CPU-second, was not met; she moved it to 2.5 on the evidence above.
**A frame to judge:** S4's first frame of the 600-district city was sent to her on 2026-10-28, with the frame before it and where they differ.
