# 214. The unfocused dashboard's layout sits right at its 1% budget once kernel time counts

**Open. Filed 2026-10-23 (r954), from item 209's quiet-machine table. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: nothing

With [item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) counting retired instructions at the bursty CoreRate plus the process's kernel ticks, on a quiet machine (load 1.3, under the landing lock), the unfocused city in [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md)'s test reads **1.04% of a core against 1%**: decoding 13 ms and layout 144 ms over 15 s and 16 snapshots. Layout counted 104 ms before the kernel term, so about 40 ms of it is in the kernel — most likely page faults from layout's allocations. [Item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md) left groups' input (~2 ms a snapshot) and the rest of `city.build` at ~7 ms a snapshot.
Item 209 lands the check as "unmet" (skip over 1% saying its number; fail over 2%), naming this item.

## The fix

Cut what a snapshot that shapes little allocates: reuse layout's buffers across snapshots, and the remaining per-snapshot passes item 206 named (groups' input). Measure allocations per snapshot before and after, and the kernel share.

Tests: item 209's unfocused check becomes a plain gate at 1% (its skip removes itself); a benchmark of allocations per activity-only snapshot.
