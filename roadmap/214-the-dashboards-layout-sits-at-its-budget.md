# 214. The unfocused dashboard's layout sits right at its 1% budget once kernel time counts

**Open, in progress since 2026-10-26 in the session "item 214". Filed 2026-10-23 (r954), from item 209's quiet-machine table. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

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
