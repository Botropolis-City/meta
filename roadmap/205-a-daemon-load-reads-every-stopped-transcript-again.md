# 205. Every rescan loads the whole catalogue again, so the daemon's cost grows with the number of sessions

**Open, in progress since 2026-10-22 in the session "item 205". Filed 2026-10-22 (r910), from items 196 and 198. Nobody's call — the budget is set (daemon ≤ 2% of a core, settled).**

Depends on: nothing

[Item 196](196-a-settled-daemon-bursts-to-several-cores-on-rescans.md) made a settled rescan cheap on a home of a few hundred sessions and left one thing named for later: **making a load incremental per file**. [Item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md) measured why it matters: on the synthetic home plus 2,000 small sessions, with one session working and a prompt every 5 s, the settled daemon uses **6.5% of a core against 2%** (at a load of ~25, so inflated). Grouping is about 0.8% of that. The rest is the per-rescan load: the collector 38% of its CPU, `Loader.catalogue` stat'ing every stopped transcript 18%, then `Build`, `events.Observe` and the transcript index — all over every session, on every rescan.

## The fix

A rescan does work in proportion to what changed: the catalogue keeps each stopped transcript's entry and re-stats only directories the watcher saw change (item 196's index already knows which); `Build` reuses the sessions whose inputs are unchanged, with a from-scratch build as the oracle, as items 158 and 197 did.

Tests: item 198's 2,000-session acceptance case turns from "unmet" into a gate at 2% (the quieter of two windows, as item 196's does); a rescan after one session writes stats no stopped transcript; built snapshots equal from-scratch at every step of a replay.

**Busy measurement** (benchmark session, 2026-10-22): with two sessions each writing a line every 200 ms, the scratch daemon used **4.7–5.1% of a core** against 2% (item 196's acceptance test, with one session on a synthetic home, passes at ≤ 2%). The per-rescan load this item names is the likely remainder; measure it with two or more writers.

**Caveat on the 4.7–5.1% busy figure** (benchmark session, 2026-10-22): the replay ran its daemon with `--home`, and since item 165 a daemon pointed at a home opens no statistics store, so it never did the per-change ingest a real daemon does. The production daemon under two writers is likely higher. The replay tool will run the daemon with a scratch `HOME` (and scratch XDG dirs) so it behaves as production; re-run this item's busy case with the store on before closing.
