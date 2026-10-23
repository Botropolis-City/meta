# 213. A settled daemon on a 2,000-session home is just over its CPU budget

**Open. Filed 2026-10-23 (r953), from item 209's quiet-machine table. Nobody's call — the budget is set (daemon ≤ 2% of a core, mean, settled).**

Depends on: nothing

[Item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) measured every cost gate on a quiet machine (load 1.8, under the landing lock), in retired instructions at the bursty CoreRate Aria chose, beside the same run's process ticks. The daemon on the synthetic home plus 2,000 small sessions, one session writing and a prompt every 5 s, read **2.32 and 2.57% of a core counted, and 1.96 and 2.22% by ticks**, against 2%. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) closed with it at 1.9% under load; on a quiet machine, counted honestly, it is over. Grouping's share per prompt is within [item 210](210-a-prompt-costs-over-50-ms-at-2000-sessions.md)'s 50 ms (about 12 ms added), so the remainder is the per-rescan load at that size.
Item 209 lands that check as "unmet" (skip over 2%, saying its number; fail over 4%), naming this item.

## The fix

Profile the settled 2,000-session daemon (counted, quiet machine) and take the largest per-rescan passes that still walk every session. Item 205's notes list the candidates left after its slices: the view copy, events, power, roads, and the collector.

Tests: item 209's check turns from "unmet" into a plain gate at 2% (its skip removes itself), on instructions plus kernel ticks.
