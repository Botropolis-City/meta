# 194. Nothing counts the work a frame takes, so a regression in drawing passes every test

**Open. Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161 and the benchmark session's measurement. Nobody's call — Aria ruled on the targets, below.**

Depends on: nothing

Item 156's measurement (`3150e0e`) counted, per frame of the metropolis demo, 478 draw commands, 175 render-target switches and 734,811 indices; forcing anti-aliasing off left the commands at 476 and cut the indices 6.6×.
So a gate on draw commands alone would have passed the build that grew the heap to gigabytes: **indices (or vertices) a frame are the count that moved**.
Every one of these is a count of work, not of seconds, so it does not change with machine load, which is the rule the acceptance tests already gate by.

## The fix

A measure test in `testing/acceptance/`, beside `frame_bench_test.go`, that drives the largest demo city headlessly to a settled frame by day and by night and counts **indices, draw commands and render-target switches** a frame, from Ebitengine's `ebitenginedebug` log or a counter in the render package.
It gates at targets, never at today's counts (gate on targets).
The first answer the item needs is the targets: the session measures, proposes them from the budget's 10 ms a frame, and Aria sets them.
Once item 193 lands, the counts should not grow with the number of buildings, and the test should say so.

It lands first, so items 191–193 can each show what they changed.

## Answered

- **The targets** (Aria, 2026-10-21: *"I don't fully understand 194, but we should do all we can"*): she does not set numbers.
  The session sets each target as tight as items 191–193 can reach, derived from the budget's 10 ms of CPU a frame on integrated graphics, never from today's count, and writes the reasoning here.
  When a fix lands, the target tightens to what it reached, so the counts can only go down.
