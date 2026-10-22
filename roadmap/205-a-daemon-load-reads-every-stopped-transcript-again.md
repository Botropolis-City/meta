# 205. Every rescan loads the whole catalogue again, so the daemon's cost grows with the number of sessions

**Open. Filed 2026-10-22 (r910), from items 196 and 198. Nobody's call — the budget is set (daemon ≤ 2% of a core, settled).**

Depends on: nothing

[Item 196](196-a-settled-daemon-bursts-to-several-cores-on-rescans.md) made a settled rescan cheap on a home of a few hundred sessions and left one thing named for later: **making a load incremental per file**. [Item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md) measured why it matters: on the synthetic home plus 2,000 small sessions, with one session working and a prompt every 5 s, the settled daemon uses **6.5% of a core against 2%** (at a load of ~25, so inflated). Grouping is about 0.8% of that. The rest is the per-rescan load: the collector 38% of its CPU, `Loader.catalogue` stat'ing every stopped transcript 18%, then `Build`, `events.Observe` and the transcript index — all over every session, on every rescan.

## The fix

A rescan does work in proportion to what changed: the catalogue keeps each stopped transcript's entry and re-stats only directories the watcher saw change (item 196's index already knows which); `Build` reuses the sessions whose inputs are unchanged, with a from-scratch build as the oracle, as items 158 and 197 did.

Tests: item 198's 2,000-session acceptance case turns from "unmet" into a gate at 2% (the quieter of two windows, as item 196's does); a rescan after one session writes stats no stopped transcript; built snapshots equal from-scratch at every step of a replay.
