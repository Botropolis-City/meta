# 207. An unfocused city redraws the whole world on every change, without the standing city

**Open. Filed 2026-10-22 (r916), from the benchmark session's busy run after item 201. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: nothing

Measured on the 265U's GPU (real history linked read-only into a scratch home, two sessions each writing a line every 200 ms, 450 s; raw in `~/.local/state/botropolis-perf/busy-unfocused-{r910,r905}-real-20261022-184541/`): **an unfocused, visible city at r910 averaged 2.74% of a core (p95 4.9%) against 1%** — r905 3.60%. It drew a frame per change, about 360–480 frames, at 12–17 ms each, **with the standing-city layer never reused**.
Where it goes (300 s profile): Draw 57% — `drawIso` 45%, a full world redraw per change; overlays 12%, text 10% — then `SetSnapshot` → `city.build` 22% ([item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md)), GL flush 7%, GC 6%.
[Item 193](193-a-still-city-is-redrawn-whole-every-frame.md) composes the standing city once and redraws only what moves; [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md)'s gate covers decoding and layout only, since Xvfb draws in software, so this draw path went unmeasured until now.

## The fix

Find why the unfocused draw-on-change path doesn't use the standing city (its key changing on every snapshot, or the path bypassing it), and make a change that moves one building redraw only that building's rectangle, as a focused frame does. Then item 206's layout work takes most of the rest.

Tests: an unfocused city fed a change to one session's state recomposes the standing layer on no frame and draws only dirty rectangles (count it in the frame log, as item 193's tests do); re-measure busy on the GPU with the benchmark session's replay, against 1%.
