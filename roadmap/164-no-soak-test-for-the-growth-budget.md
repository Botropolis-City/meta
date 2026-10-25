# 164. No 8-hour soak test exists, so the growth budget has never been measured

**Open. Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the growth budget Aria set the same day. Nobody's call — the budget is set; the run that checks it is missing.**

Depends on: 245
Landed: slice 1 (`fe9ea57`, r1028).

[budgets.md](../performance/budgets.md) sets the city's growth at **≤ 1 MiB an hour of `Private_Dirty` + GPU**, measured by "an 8-hour soak with sessions working, before each release".
No such run exists.
The longest any report has sampled is 15 minutes ([the laptop report](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md); [the 265U report](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md)), and a 15-minute slope is mostly start-up: method.md says to call nothing a leak unless its slope holds over a long run.
Both reports say a slow leak after the start-up burst would not show.

There is also no release checklist to put it on.
The release is described in `botropolis/CLAUDE.md` and run by the release workflow, which runs `make bench` but nothing that takes hours on a real display.

## The fix

1. A soak mode for `perf-city`: `--seconds 28800` already works, but the run needs sessions working for its whole length and a window that stays visible and drawing for part of it and hidden for the rest, or it measures only one of the two.
   It should record the slope of `Private_Dirty` + `gpu_mib` per hour after the first 10 minutes, for the city and the daemon, and fail when either is over the budget.
2. A release checklist, in `botropolis/` beside the release section of its `CLAUDE.md`, with the soak as a step that a release does not ship without, its report written to `performance/reports/`.
   Aria's ruling that demo and website frames are re-filmed once per release, not per item, belongs on the same list.

Run it once against the release in hand when it lands, and file whatever grows.

**Lead from item 163's close** (r905): a hidden city's own memory rose 31 MiB over five minutes while its Go heap held at 90–96 MB; the soak should show whether that keeps climbing.

## Answered while building

- **When the soak runs** (Aria, 2026-10-25, asked by the manager): build the soak mode and the release checklist now, then run the 8 hours overnight, while Aria is away from the machine, never while she works at it. The session asks the manager for a night before starting the run.
- **The plan** (manager, 2026-10-25): approved. `perf-soak` in `performance/tools` on top of `perf-busy-city`, visible for the first half and hidden for the second, a slope per process per phase at ≤ 1 MiB/h for the city and the daemon alike (the item says "either"), one switch at half-way, no landing lock (the load is recorded instead), and `RELEASING.md` in botropolis.
- **A screen that blanks or locks overnight** (Aria, 2026-10-25, asked by the manager): she asked whether the soak could run in a VM instead of leaving the laptop unlocked; the trade-off (a VM's GPU is not this laptop's) is with her, and the soak takes its display as a parameter meanwhile.
