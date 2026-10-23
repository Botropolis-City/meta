# 205. Every rescan loads the whole catalogue again, so the daemon's cost grows with the number of sessions

**Fixed 2026-10-23 (`e6b8b07`, r939). Filed 2026-10-22 (r910), from items 196 and 198. Nobody's call — the budget is set (daemon ≤ 2% of a core, settled).**

Depends on: nothing
Landed: slice 1 (`181b868`, r922).
Landed: slice 2 (`f81791d`, r923).
Landed: slice 3 (`b8b5ff2`, r924).
Landed: slice 4 (`083f60e`, r936).
Landed: slice 5 (`06f5565`, r937).
Landed: slice 6 (`22d894a`, r938).
Landed: slice 7 (`e6b8b07`, r939).

[Item 196](196-a-settled-daemon-bursts-to-several-cores-on-rescans.md) made a settled rescan cheap on a home of a few hundred sessions and left one thing named for later: **making a load incremental per file**. [Item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md) measured why it matters: on the synthetic home plus 2,000 small sessions, with one session working and a prompt every 5 s, the settled daemon uses **6.5% of a core against 2%** (at a load of ~25, so inflated). Grouping is about 0.8% of that. The rest is the per-rescan load: the collector 38% of its CPU, `Loader.catalogue` stat'ing every stopped transcript 18%, then `Build`, `events.Observe` and the transcript index — all over every session, on every rescan.

## The fix

A rescan does work in proportion to what changed: the catalogue keeps each stopped transcript's entry and re-stats only directories the watcher saw change (item 196's index already knows which); `Build` reuses the sessions whose inputs are unchanged, with a from-scratch build as the oracle, as items 158 and 197 did.

Tests: item 198's 2,000-session acceptance case turns from "unmet" into a gate at 2% (the quieter of two windows, as item 196's does); a rescan after one session writes stats no stopped transcript; built snapshots equal from-scratch at every step of a replay.

**Busy measurement** (benchmark session, 2026-10-22): with two sessions each writing a line every 200 ms, the scratch daemon used **4.7–5.1% of a core** against 2% (item 196's acceptance test, with one session on a synthetic home, passes at ≤ 2%). The per-rescan load this item names is the likely remainder; measure it with two or more writers.

**Caveat on the 4.7–5.1% busy figure** (benchmark session, 2026-10-22): the replay ran its daemon with `--home`, and since item 165 a daemon pointed at a home opens no statistics store, so it never did the per-change ingest a real daemon does. The production daemon under two writers is likely higher. The replay tool will run the daemon with a scratch `HOME` (and scratch XDG dirs) so it behaves as production; re-run this item's busy case with the store on before closing.

## Decided while working

- **Four slices** (the roadmap manager, for Aria, 2026-10-22): the ledger's saves, the catalogue's stats, `Build`'s reuse, then the O(n) passes after it until the 2,000-session gate passes.
- **A change that only moves a session's last activity is saved at most once a minute**, and when the daemon stops; a new session, a pack, an unpack or a demolish is saved at once.
  The trade is stated in a test: a daemon killed without shutting down loses at most a minute of last-activity times.
- **The catalogue trusts the watcher's events for stopped transcripts**, which deviates from item 196, which chose modification times over events so that filesystems with no inotify still work.
  Those keep today's behaviour: a directory the watcher could not hold is looked at in full on every rescan, and logged once, loudly; so is every directory after an overflow, and with no watcher at all.
  A rolling audit looks at a sixtieth of the trusted transcripts each rescan, so a missed event shows within 60 rescans.
  The watcher holds every project directory, not only those a live session is in.
- **The daemon budget tests move to a scratch `HOME` in slice 4.**
  This item's test and items 157's and 196's ran with `--home`, so they opened neither the statistics store nor the ledger.
  One helper starts the daemon as production does and asserts that the store and the ledger opened and were written during the run.
  Before and after numbers for all three, store off and on, are reported; a gate that goes red with the store on is a miss to fix here, not a limit to raise.
  The helper lands last, once the gates it turns on can pass.
- **The store's ingest is made incremental here** (slice 5): with the store on, every stats pass walked every transcript, and each pass that moved a heft started a rescan at once, so with a session writing the rescans outran the pace.
  The loader hands the pass the files it saw change; a full ingest still runs on the first pass and every 10 minutes.
- **Transcript rescans are paced by their own cost** (the roadmap manager, 2026-10-22), a change to item 196's one-a-second rule: after each, the next waits until it has cost at most 1% of a core, at least 1 s and at most 5 s.
  The cost is the rescan's own thread CPU, so under load the pace slows, which is the safe direction.
  Hooks still change a building at once; on a home that needs more than 5 s to hold 1%, the gate shows it unmet rather than the lag growing.
- Slices from here: 4, the passes after `Build` that still copy every session; 5, the incremental ingest; 6, the paced rescans; 7, the helper and the three gates.

## Measured

- Slice 1: a busy load (the synthetic home plus 2,000 sessions, one appending a reply each load, a prompt every fifth) fell from about 90 ms of CPU to 52 ms, where 2% of a core at one rescan a second is 20 ms.
  Before it, `TestDaemonWithTwoThousandSessions` used 6.6–9.0% of a core at a load of 12–15, with `--home`, so without the store or the ledger.
- Slices 2 and 3: the same load fell to about 30 ms, then 18–20 ms, and what it allocates from 11 MB to 6.
- **With the store on** (main before this item, `b34cc7e`, load 5–13): item 157's test 0.5% of a core (0.2% off); item 196's 4.4–5.6% (0.8% off), failing; this item's 2,000 sessions 45% (5.3% off) and 78 MiB of Private_Dirty, failing both.
  In a scratch build of slices 2–5 with the pass's rescans paced, item 196's was 1.1–1.2% and the 2,000 sessions 3.0–3.3%.
- **The busy re-run owed at close.** On the real history, busy (2026-10-23, the benchmark session): `perf-busy-city` at meta `a0d8888`, so the daemon runs on a scratch `HOME` with the statistics store on, settled first (idle after 100–121 s);
  211 transcripts linked read only, two writers a line every 200 ms for 455 s, the city visible and unfocused after 20 s, load 1.2–8.8, monitor on.
  r946's daemon used **2.36% of a core** (p50 0.0%, p95 10.5%) and 54–55 MiB of Private_Dirty, flat (+0.13 MiB a minute); r910's, before this item, 9.34% (p95 12.6%) and 54 MiB.
  So the real busy desk costs a quarter of what it did, and is still over the 2% budget, where the gate at 2,000 synthetic sessions reads 1.8–2.0% and 62–63 MiB.
  The installed daemon, built before this item, burst to 3.7 cores during r946's half and the load rose to 7–9, so r946's figure is the less favourable of the two.
  Raw runs: `~/.local/state/botropolis-perf/busy-r946-r910-20261023-061028/`.

## Closed

Fixed in seven slices in botropolis, with the changelog entry (`d201840`) and a fix to item 208's release tests, which slept in real time (`43d9545`), after them:
- `181b868` (r922): the ledger saves a change to last activity alone at most once a minute, and on shutdown, and no longer reads its own file back before a save.
- `f81791d` (r923): the watcher tells the loader which files changed and holds every project directory, so a rescan stats only the stopped transcripts that changed, plus a rolling sixtieth of the rest.
- `b8b5ff2` (r924): the catalogue keeps its entries in place, and the built stopped sessions are kept while none of them changes.
- `083f60e` (r936): the passes after `Build` that copied or hashed every session (the event log, the harness list, the group signature, the plant's power, the transcript index, group views) do so no longer, and a background stats pass asks the watcher for a rescan instead of rescanning at once.
- `06f5565` (r937): a stats pass ingests only the transcripts the loader saw change, with a full ingest first and every 10 minutes.
- `22d894a` (r938): transcript rescans are paced by their own thread CPU to 1% of a core, between 1 s and 5 s.
- `e6b8b07` (r939): the daemon budget tests of items 157, 196 and this one run a person's own daemon, on a scratch `HOME` with the store and the ledger, and check both were written.

The tests that show it:
- `TestLoadsEqualFromScratch` holds the loader, told what a watcher would say, to a loader starting from nothing at every step of three replays of 150 steps; `TestIngestPathsEqualsIngest` holds the store's ingest by path to a full ingest over three replays of 120.
- `TestCatalogueStats` (a rescan after one write stats that transcript and the audit's share, and everything with no watcher, after an overflow or in an unwatched directory), `TestStatsPassIngestsWhatChanged`, `TestLoaderSavesTheLedger`, `TestWatchPacesByCost` and `TestRequestRescan`.
- `TestDaemonWithTwoThousandSessions` gates at 2%: 1.8–2.0% of a core with the store open, where main before this item used 45%.
  Item 196's test reads 1.0–1.1% with the store (4.4–5.6% before), item 157's 0.5%.

Every new check was mutated and the mutants fail, apart from one: a newly watched directory's extra look is caught by `TestCatalogueStats` but not by the replay, which always reports its writes.

Deviations, all agreed with the roadmap manager:
- **Transcript rescans are paced by their own cost**, a change to item 196's one-a-second rule; hooks still change a building at once, and nothing read from a transcript is more than 5 s late.
- **The catalogue trusts the watcher's events** where item 196 chose modification times, with the rolling audit and full looks as the backstop.
- **The store's ingest was made incremental here** (slice 5), because opening the store, as the tests had not, showed it was most of the cost.
- **Item 157's test now measures from when the daemon has settled**, since with the store open a fresh daemon starts its first-launch ingest.
- Two gates skip while over their limits and fail over a ceiling: Private_Dirty at 2,000 sessions with the store open, 62–63 MiB against 64 and 80 at most, is [item 211](211-the-statistics-store-adds-21-mib-at-2000-sessions.md); a prompt's whole next load at 2,000 sessions, 31–60 ms against 50 and 90 at most, is [item 210](210-a-prompt-costs-over-50-ms-at-2000-sessions.md).

Owed: the benchmark session's busy re-run with the store on, at r939 or later, which it appends under *Measured* when the machine is quiet.
