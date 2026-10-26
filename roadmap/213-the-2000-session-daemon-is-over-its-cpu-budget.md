# 213. A settled daemon on a 2,000-session home is just over its CPU budget

**Open, in progress since 2026-10-26 in the session "item 213". Filed 2026-10-23 (r953), from item 209's quiet-machine table. Nobody's call — the budget is set (daemon ≤ 2% of a core, mean, settled).**

Depends on: nothing
Landed: slice 1 (`8e88ccf`, r1080).

[Item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) measured every cost gate on a quiet machine (load 1.8, under the landing lock), in retired instructions at the bursty CoreRate Aria chose, beside the same run's process ticks. The daemon on the synthetic home plus 2,000 small sessions, one session writing and a prompt every 5 s, read **2.32 and 2.57% of a core counted, and 1.96 and 2.22% by ticks**, against 2%. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) closed with it at 1.9% under load; on a quiet machine, counted honestly, it is over. Grouping's share per prompt is within [item 210](210-a-prompt-costs-over-50-ms-at-2000-sessions.md)'s 50 ms (about 12 ms added), so the remainder is the per-rescan load at that size.
Item 209 lands that check as "unmet" (skip over 2%, saying its number; fail over 4%), naming this item.

## The fix

Profile the settled 2,000-session daemon (counted, quiet machine) and take the largest per-rescan passes that still walk every session. Item 205's notes list the candidates left after its slices: the view copy, events, power, roads, and the collector.

Tests: item 209's check turns from "unmet" into a plain gate at 2% (its skip removes itself), on instructions plus kernel ticks.

## Answered while building

- **Where the CPU goes, and the plan** (item 213's session and the manager, 2026-10-26): reproduced at 2.54–3.11% counted; a profile puts the statistics store's ingest at 18% of the daemon (12% SQLite parsing statements prepared afresh on every write, since modernc keeps no statement cache), GC 20%, grouping 16%, and the ledger and catalogue walks 7.6% each. Slices: prepared statements once per store; then the largest remaining whole-session walk, with a from-scratch oracle as items 205 and 210 had; then grouping views only when groups change; and last, item 209's skip comes out so the test is a plain gate at 2%.
- **What the rescan pace counts** (manager, 2026-10-26; the manager set item 205's pace on 2026-10-22): the pace held rescans to 1% of a core by their thread CPU, which counted as about 1.4% under Aria's definition of a core (instructions at the bursty CoreRate plus kernel), so cheaper rescans only ran more often. It now paces on the counted cost, the same 1% share measured as the gates measure it, with thread CPU as the fallback where there are no counters; the 5 s cap and the hooks' immediate path stay. On this home a transcript-only change can show up to about 1.3 s later (rescans every ~2.9 s, from ~1.6 s), which the later slices' cheaper rescans are to win back; the item reports the interval and the latency before and after.
