# 205. Every rescan loads the whole catalogue again, so the daemon's cost grows with the number of sessions

**Open, in progress since 2026-10-22 in the session "item 205". Filed 2026-10-22 (r910), from items 196 and 198. Nobody's call — the budget is set (daemon ≤ 2% of a core, settled).**

Depends on: nothing
Landed: slice 1 (`181b868`, r922).
Landed: slice 2 (`f81791d`, r923).
Landed: slice 3 (`b8b5ff2`, r924).

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
