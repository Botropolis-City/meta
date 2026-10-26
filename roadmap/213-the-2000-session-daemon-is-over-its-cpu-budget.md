# 213. A settled daemon on a 2,000-session home is just over its CPU budget

**Open, in progress since 2026-10-26 in the session "item 213". Filed 2026-10-23 (r953), from item 209's quiet-machine table. Nobody's call — the budget is set (daemon ≤ 2% of a core, mean, settled).**

Depends on: nothing
Landed: slice 1 (`8e88ccf`, r1080).
Landed: slice 2 (`bf1c169`, r1083).
Landed: slice 3 (`6397662`, r1085).
Landed: slice 4 (`174cdbd`, r1086).
Landed: slice 5 (`e458c9f`, r1089).

[Item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) measured every cost gate on a quiet machine (load 1.8, under the landing lock), in retired instructions at the bursty CoreRate Aria chose, beside the same run's process ticks. The daemon on the synthetic home plus 2,000 small sessions, one session writing and a prompt every 5 s, read **2.32 and 2.57% of a core counted, and 1.96 and 2.22% by ticks**, against 2%. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) closed with it at 1.9% under load; on a quiet machine, counted honestly, it is over. Grouping's share per prompt is within [item 210](210-a-prompt-costs-over-50-ms-at-2000-sessions.md)'s 50 ms (about 12 ms added), so the remainder is the per-rescan load at that size.
Item 209 lands that check as "unmet" (skip over 2%, saying its number; fail over 4%), naming this item.

## The fix

Profile the settled 2,000-session daemon (counted, quiet machine) and take the largest per-rescan passes that still walk every session. Item 205's notes list the candidates left after its slices: the view copy, events, power, roads, and the collector.

Tests: item 209's check turns from "unmet" into a plain gate at 2% (its skip removes itself), on instructions plus kernel ticks.

## Answered while building

- **Where the CPU goes, and the plan** (item 213's session and the manager, 2026-10-26): reproduced at 2.54–3.11% counted; a profile puts the statistics store's ingest at 18% of the daemon (12% SQLite parsing statements prepared afresh on every write, since modernc keeps no statement cache), GC 20%, grouping 16%, and the ledger and catalogue walks 7.6% each. Slices: prepared statements once per store; then the largest remaining whole-session walk, with a from-scratch oracle as items 205 and 210 had; then grouping views only when groups change; and last, item 209's skip comes out so the test is a plain gate at 2%.
- **What the rescan pace counts** (manager, 2026-10-26; the manager set item 205's pace on 2026-10-22): the pace held rescans to 1% of a core by their thread CPU, which counted as about 1.4% under Aria's definition of a core (instructions at the bursty CoreRate plus kernel), so cheaper rescans only ran more often. It now paces on the counted cost, the same 1% share measured as the gates measure it, with thread CPU as the fallback where there are no counters; the 5 s cap and the hooks' immediate path stay. On this home a transcript-only change can show up to about 1.3 s later (rescans every ~2.9 s, from ~1.6 s), which the later slices' cheaper rescans are to win back; the item reports the interval and the latency before and after.

## Measured

All on `TestDaemonWithTwoThousandSessions` (the synthetic home plus 2,000 small sessions, one writing a reply every 200 ms and a prompt every 5 s), two windows of 30 s each, counted, beside its ticks.

- **Before** (main at `a555de7`, load 2–15): 2.54/3.03%, 2.89/3.11%, 2.70/2.91% and 2.57/3.23% of a core (1.99–2.52% by ticks).
  Rescans every ~1.6 s (36–38 a minute), so a transcript-only change showed within ~1.6 s, ~0.8 s on average.
- **Slice 1** (prepared statements): CPU time fell (ticks ~2.2% to ~1.95%, the store's ingest from 18% of the profile to 7%), but counted barely moved, 2.51/2.48% and 2.58/2.91%, because a cheaper rescan only ran more often.
- **Slice 2** (pace by counted cost), loads 1–11, three runs: 1.68/1.84%, 1.78/1.87% and 1.71/1.86% (1.43–1.56% by ticks).
  Rescans every ~2.7 s (22 a minute), so a transcript-only change shows within ~2.7 s, ~1.4 s on average: **about 1.1 s later at worst and 0.6 s on average** than before.
  Hooks still change a building at once.
- Per rescan, by instructions at slice 1: grouping 15 M (detection 24 M on each of the ~10 prompts a minute; its views 4.7 M on every rescan), the ledger walk 9.6 M, the catalogue 9.2 M, servers, skills and roads 4.5 M, of about 45 M.
  The ledger and catalogue walks copy each 976-byte `Session` several times; `mergeSessions` and `Daemon.view` each copy the whole 2,000-session slice, half of the 7 MB a rescan allocates.
- **Slices 3 and 4** (manager, 2026-10-26): slice 3 lets the catalogue look only at the paths the watcher changed plus its audit's share while the listing, the live set and the held directories are unchanged, and walks the ledger without copying sessions; item 205's oracle now reaches that quiet path, and four mutants fail it. Slice 4 hands every subscriber the loaded sessions without copying them when no hook overlay applies, guarded by a test that no consumer writes to the shared slice (mutated red) and by `-race`; it adds a performance-tier gate that a rescan of the settled 2,000-session home costs under 16 ms of a core (counted, median of 5), so rescans stay about 1.6 s apart. Slice 5 makes `TestDaemonWithTwoThousandSessions` a plain gate at 2%.
- **The last cuts** (manager, 2026-10-26): five clean runs at slice 4's head read 1.67–1.76% on the gated window. Copying the merged session slice is 41% of allocation but only about 0.1 point of CPU, and reusing it needs a pool that knows when the last subscriber let go, so it is dropped as not worth its risk. Two small allocation cuts come instead (the statistics pass's hefts map clone and the event log's map rebuild, each held by an allocation-count test). Then the performance manager's 5+5 interleaved check against 071a6ae, and the plain gate at 2% only if every run after is under it and its worst beats the best before.
