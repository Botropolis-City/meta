# 214. The unfocused dashboard's layout sits right at its 1% budget once kernel time counts

**Fixed 2026-10-26 (`539a36b`, r1093). Filed 2026-10-23 (r954), from item 209's quiet-machine table. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: nothing
Landed: slice 1 (`d118583`, r1092).
Landed: slice 2 (`539a36b`, r1093).

With [item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) counting retired instructions at the bursty CoreRate plus the process's kernel ticks, on a quiet machine (load 1.3, under the landing lock), the unfocused city in [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md)'s test reads **1.04% of a core against 1%**: decoding 13 ms and layout 144 ms over 15 s and 16 snapshots. Layout counted 104 ms before the kernel term, so about 40 ms of it is in the kernel — most likely page faults from layout's allocations. [Item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md) left groups' input (~2 ms a snapshot) and the rest of `city.build` at ~7 ms a snapshot.
Item 209 lands the check as "unmet" (skip over 1% saying its number; fail over 2%), naming this item.

## The fix

Cut what a snapshot that shapes little allocates: reuse layout's buffers across snapshots, and the remaining per-snapshot passes item 206 named (groups' input). Measure allocations per snapshot before and after, and the kernel share.

Tests: item 209's unfocused check becomes a plain gate at 1% (its skip removes itself); a benchmark of allocations per activity-only snapshot.

## Answered while building

- **Where it stands at starting** (manager, 2026-10-26): `make test-performance` at r1089 read the unfocused city at 0.84% of a core, the first quiet reading under 1% since this item was filed; the work may now be mostly proving it, as item 213 did, with five quiet runs interleaved with a build from before (the performance manager's runner), before the skip comes out and the check becomes a plain gate at 1%. If the margin is too thin, the item's own fix (layout's buffers reused across snapshots, allocations per activity-only snapshot measured) comes first.
- **The plan and its proof** (manager, 2026-10-26): gate-only. The skip and the 2% unmet ceiling come out of `hidden_cost_test.go`, and both unfocused cases become plain gates at 1%, with no change to production code; buffer reuse was this item's means, and other items' work met the end first. The proof is ten quiet runs of the code as it stands, every one under 1% in both unfocused cases and the worst at most 0.95%, since on unchanged code the question is whether the gate holds without flaking, not whether the code got cheaper.
- **A change only the performance tier can see** (manager, 2026-10-26): `make land` refused the gate commit, because its change-selected acceptance run picked only this performance-tier test, the landing run drops that tier, and an empty pool fails. `test-acceptance-changed` now splits a selection by tier, names each performance test it leaves to `make test-performance`, and passes when nothing else is left; every other empty run still fails. Such a change's gate is the performance manager's quiet runs, which for this item were ten, all under 1%.

## Closed

Fixed in two slices in botropolis, with no change to the city's own code: other items' work had already brought it under budget.

- `d118583` (r1092): `make land`'s acceptance step names each performance-tier test a change reaches and leaves it to `make test-performance`, and passes when nothing else was selected, where an empty run had failed; every other empty run still fails.
  `TestOutsideTier` holds the split, and the old behaviour, every selected test run, failed four of its five cases.
- `539a36b` (r1093): both unfocused cases of `TestAnUnwatchedCityUnderAStreamOfSnapshots` are plain gates at 1% of a core, counted in instructions with kernel time, with item 209's skip and 2% ceiling gone.
  With the budget mutated to 0.5%, both failed, at 0.79% and 0.82%, where the skip would have hidden them.
  It landed through the new path: "not run here: the performance tier … TestAnUnwatchedCityUnderAStreamOfSnapshots".

**A performance-only change's gate is the performance manager's quiet runs, not `make land`'s**, and this is now how such a change lands.

**The check** (the performance manager, 2026-10-26, ten quiet runs at `3abe37a`, the code the gate landed on; raw in `~/.local/state/botropolis-perf/item-214-10runs-20261026-083831/`):

| run | load | hidden | unfocused, 15 s | unfocused, over the store, 65 s |
| --- | --- | --- | --- | --- |
| 1 | 2.20 | 0.43% | 0.87% | 0.79% |
| 2 | 0.96 | 0.37% | 0.82% | 0.79% |
| 3 | 0.92 | 0.43% | 0.92% | 0.80% |
| 4 | 1.98 | 0.37% | 0.82% | 0.84% |
| 5 | 2.11 | 0.37% | 0.81% | 0.76% |
| 6 | 1.20 | 0.43% | 0.79% | 0.77% |
| 7 | 0.95 | 0.43% | 0.81% | 0.78% |
| 8 | 1.32 | 0.50% | 0.84% | 0.80% |
| 9 | 1.45 | 0.43% | 0.81% | 0.80% |
| 10 | 2.48 | 0.30% | 0.83% | 0.82% |

Every run is under 1% in both unfocused cases, and the worst is 0.92%.
**Caution, from the performance manager:** the 15 s case has the thinner margin, 0.08 points at its worst, so it is the one to watch if the dashboard's unfocused work grows.

**For Aria — deviations from what the item asked:**

- **Layout's buffers were not reused.** That was the item's means to the 1% gate, and other items' work reached the gate first.
  Whoever wants more margin starts from item 206's `BenchmarkSetSnapshot/activity-only`: 3.56 ms, 3.2 MB and 5,343 allocations a snapshot today, spread across `city.build` (placing streets 29%, ordering sites 12%, districts 12%, buildings 8%, the ground 7%) with no single large piece.
- **No new allocation benchmark.** Item 206's activity-only benchmark already reports allocations a snapshot, so it is cited rather than duplicated.
