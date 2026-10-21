# 194. Nothing counts the work a frame takes, so a regression in drawing passes every test

**Done 2026-10-21 (`8acbbbb`, r845). Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161 and the benchmark session's measurement. Nobody's call — Aria ruled on the targets, below.**

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

## The counts and the targets

Measured at r844 (`bd67029`), the worst settled frame, 1600×900, headless (Xvfb, llvmpipe):

| demo | draw commands | indices | render-target switches |
| --- | --- | --- | --- |
| metropolis, day | 421 | 751,662 | 165 |
| metropolis, night | 480 | 762,564 | 171 |
| hamlet, day (3 sessions) | 199 | 124,386 | 84 |
| an empty city, day | 60 | 15,318 | 27 |

**The targets** (the session, approved by the roadmap manager for Aria, 2026-10-21), for the metropolis by day and by night: **≤ 20,000 indices, ≤ 70 draw commands, ≤ 30 render-target switches a frame**; and once item 193 lands, the metropolis at no more than 1.25× the hamlet on each count.

- **What 191–193 can reach.** After them a still frame is the empty city's floor — chrome, ground and plant, about 60 commands, 15,000 indices and 27 switches — plus one copy of the cached layer and the movers as stamps, about 100 movers at 6 indices each.
  191–193 do not touch the chrome's switches, so 30 is as tight as they reach.
- **The 10 ms budget.** With rough per-unit CPU costs on integrated graphics — about 20 µs a command, 50 µs a target switch and 10 ns an index, estimates for `perf-city` to check when 191 lands — the targets cost about 1.4 + 1.5 + 0.2 ≈ 3 ms of submitting, leaving about 7 ms for updating, sorting and text.
  The same model puts r844 at about 24 ms of submitting alone, the same order as the 41 ms item 161 measured on the laptop.

**How it gates** (the roadmap manager, 2026-10-21): a target gated now would block every landing for days, and a ceiling alone would let the gap live only in a table, as item 91's did.
So each count has both.
A **target case** asserts the target; while the count is over it, it skips with `unmet: N against target T`, so every run prints the gap, and **once the count meets the target the case fails** with `target met: remove the skip`, so the skip cannot outlive the fix.
A **ceiling case** under it gates: *it should issue no more … a frame than it did at r844*, at r844's worst plus 2%, lowered by each of 191, 192 and 193 to what it reached.

## Closing

Done in `8acbbbb` (r845): `TestTheWorkAFrameTakes` in `testing/acceptance/framework_test.go`, with the log parser in `testing/helpers/framelog.go` and its unit tests, and a paragraph in `botropolis/design/what-it-costs.md`.
It builds the city with `-tags 'devtools ebitenginedebug'`, records one second of the metropolis demo headless at 1600×900, by day and by night in parallel, and takes the worst of frames 10 to 34; day and night are set with `TZ` so the local hour reads 14 or 22, with no key presses.
It costs about 110 s of wall clock in the acceptance suite, most of it llvmpipe drawing the anti-aliased fills; that should fall as 191 lands.

Deviations, flagged for Aria:

- **Not in-process.** A driven city drops every draw before Ebitengine's queue sees it (`pkg/render/drive_deferred.go`), so it cannot count indices; the test runs the real city instead.
- **The hamlet comparison is item 193's to add**, since it can only pass once 193 lands.

Mutated red before landing: a ceiling below r844's count failed, and a target already met failed with `target met: remove the skip`.
A parser that matched nothing would read zero a frame, which also fails the target cases.

Item 193 does not close while any target case in `TestTheWorkAFrameTakes` still skips.
