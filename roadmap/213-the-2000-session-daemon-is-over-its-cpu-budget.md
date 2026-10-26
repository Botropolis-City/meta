# 213. A settled daemon on a 2,000-session home is just over its CPU budget

**Fixed 2026-10-26 (`85a3ce3`, r1090). Filed 2026-10-23 (r953), from item 209's quiet-machine table. Nobody's call — the budget is set (daemon ≤ 2% of a core, mean, settled).**

Depends on: nothing
Landed: slice 1 (`8e88ccf`, r1080).
Landed: slice 2 (`bf1c169`, r1083).
Landed: slice 3 (`6397662`, r1085).
Landed: slice 4 (`174cdbd`, r1086).
Landed: slice 5 (`e458c9f`, r1089).
Landed: slice 6 (`85a3ce3`, r1090).

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

## Closed

Fixed in six slices in botropolis, with the changelog entry in `3abe37a` (r1091):

- `8e88ccf` (r1080): the statistics store prepares the statements an ingest runs once a store, where every write compiled its SQL again (modernc keeps no statement cache).
- `bf1c169` (r1083): transcript rescans are paced by what they cost a core as the gates count one, instructions at CoreRate plus kernel time, with thread CPU only where nothing can be counted; the share, the 1 s floor, the 5 s cap and the hooks' immediate path are unchanged.
- `6397662` (r1085): while nothing was listed or moved, a rescan's catalogue walks only what the watcher named and the audit's sixtieth, and the ledger walk works on the sessions in place.
- `174cdbd` (r1086): a view shares the loaded sessions until a hook has something to say about one, instead of copying all 2,000 on every rescan and hook event.
- `e458c9f` (r1089): the statistics pass changes its map of hefts in place (a load reads it under the lock), and the event log keeps two maps and swaps them.
- `85a3ce3` (r1090): `TestDaemonWithTwoThousandSessions` gates at 2% of a core, on the quieter of its two windows as before, with item 209's skip and 4% ceiling gone; its home and stream are unchanged.

**The check** (the performance manager, 2026-10-26, five quiet runs at each build, interleaved; raw in `~/.local/state/botropolis-perf/item-213-5x5-20261026-075113/`), gated window, then the other, with ticks:

| run | before, `071a6ae` | after, `e458c9f` |
| --- | --- | --- |
| 1 | 2.66% (2.79, 2.66; ticks 2.36, 2.26) | 1.65% (1.65, 1.99; ticks 1.53, 1.59) |
| 2 | 2.80% (2.80, 3.30; ticks 2.23, 2.53) | 1.75% (1.75, 1.76; ticks 1.69, 1.63) |
| 3 | 2.54% (2.54, 3.29; ticks 2.19, 2.56) | 1.67% (1.67, 1.79; ticks 1.46, 1.69) |
| 4 | 2.98% (2.98, 2.98; ticks 2.29, 2.43) | 1.79% (1.79, 1.96; ticks 1.63, 1.66) |
| 5 | 2.72% (2.72, 2.80; ticks 2.29, 2.33) | 1.75% (1.75, 1.77; ticks 1.63, 1.60) |

Every after-run is under 2%, and the worst of them, 1.79%, is under the best before-run, 2.54%: about a point lower, 37%, by counted instructions and by ticks alike.
**Caution, from the performance manager:** the other window read 1.99% and 1.96% in two of the five pairs, so a gate on either window, or on the mean of the two, would sit at its edge; the gate stays on the quieter window, as it judged before this item.

The tests that show it:

- `TestARescanAtTwoThousandSessions` gates a rescan on that home at 16 ms of a core, counted, median of five, so the pace rescans about every 1.6 s: 9.7–10.7 ms now, 16.3 ms on the code before slices 3 and 4.
- `TestWatchPacesByCost` steps the watch's clock and asserts the wait it asks for: counted cost paces where thread CPU would not, thread CPU where nothing is counted, and a hook reaches subscribers before the next rescan at the 5 s cap; `TestCounted` counts whatever the tests' switch says.
- `TestCatalogueStats` counts the transcripts walked, and item 205's `TestLoadsEqualFromScratch` now reaches quiet loads (the quiet check compares the listing's contents; before that the replay never reached one, since the index shares its listing only once a directory has been quiet 2 s).
- `TestViewSharesTheLoadedSessions` and `TestSharedViewsAreNotWrittenTo`, which hands a shared view to every consumer, in the daemon and through its socket, and holds the loaded sessions to a deep copy taken before any saw them; `pkg/daemon` passes under `-race`.
- `TestSavePreparesOnce`, `TestStoredHeftsPass` (with a `-race` case of loads beside passes) and `TestObserveAllocations`.

Mutants, each shown red:

- the quiet catalogue ignoring the watcher's changes: `TestLoadsEqualFromScratch` at seeds 205, 206 and 207, and `TestCatalogueStats`;
- the quiet catalogue skipping the audit: `TestCatalogueStats` (a missed change read within 60 loads);
- a quiet load after the live set changed: `TestLoadsEqualFromScratch` at seeds 205, 206 and 207, and `TestCatalogueStats`'s live session that stops;
- a quiet load after the watcher drops a directory: `TestCatalogueStats`'s two dropped-directory cases;
- the pace on thread CPU again, an event log that writes one field of a shared view, a load reading the hefts outside the lock (the race detector), and one ingest statement compiled again.

**For Aria — deviations from what the item asked:**

- **The rescan pace changed what it counts** (the manager, for you, 2026-10-26). Item 205's 1% share was measured by thread CPU, about 1.4% under your definition of a core, so rescans alone took most of the 2% budget, and making them cheaper only made them more frequent. Pacing by the counted cost put rescans ~2.7 s apart (from ~1.6 s), so a transcript-only change showed up to ~1.1 s later; slices 3 and 4 cut a rescan from ~45 M instructions to ~30 M, and rescans are ~1.6–1.7 s apart again. Hooks were never delayed.
- **`mergeSessions`' copy of the 2,000 sessions stays** (the manager, 2026-10-26). It costs 0.34 M instructions a rescan; its whole cost is the 2 MB it allocates, about a tenth of a point of collector work. Each load writes into that slice and then shares it with every client, so reusing it needs a pool that knows when the last holder, a slow client mid-encode included, lets go, or a smaller `Session`: both large and risky for 0.1 points. It was dropped for the two small collector cuts in slice 5.
- **The remaining cost is mostly by design.** Above ~10 ms a rescan, the pace holds rescans at their 1% share whatever they cost, and a rescan here is ~15 ms (grouping's views 4.7 M instructions every rescan, roads 4.2 M, the ledger 4.8 M, detection ~9 M averaged over the prompts). Under ~10 ms the 1 s floor takes over and cheaper rescans would show; that is where more margin is, if the budget ever needs it.
