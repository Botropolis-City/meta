# 157. The daemon's 16 MiB heap cap and a forced release after every rescan keep it collecting garbage

**Open, in progress since 2026-10-21 in the session "item 157". Filed 2026-10-19 (r780), from the 0.2.2 performance reports. Nobody's call — a defect against the daemon budgets.**

Depends on: nothing

The daemon caps its own Go heap at 16 MiB (`DefaultMemoryLimit`, `pkg/appd/daemon.go:42`, set in `RunDaemon` unless `GOMEMLIMIT` is in the environment), and `Daemon.Rescan` calls `debug.FreeOSMemory()` after every load (`pkg/daemon/daemon.go:226`).
Its live heap sits near the cap whenever it works, so the collector runs continuously.

**What it costs**, from [the laptop report](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md) (Core Ultra 7 255H) and [the Core Ultra 7 265U report](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md):

- **~61% of the daemon's CPU is the garbage collector**: 1,474 collections a minute against 19 for 0.1.7 (laptop, A/B over five minutes).
- Side by side in the same five minutes, `GOMEMLIMIT=256MiB` took 0.2.2 from **6.3% of a core to 0.6%**, and p95 from 45% to 4.5%, for 0.8 MiB more `Private_Dirty`.
- First launch on the 265U: **10,778 collections, 32 CPU-seconds, a peak of 358% of a core**; with `GOMEMLIMIT=256MiB`, 357 collections, 10.8 CPU-seconds, a peak of 115%. The same 3.6 GB was read either way.
- Settled with no hook pushes on the 265U: 41 collections a minute against 2.6 for 0.1.7.
- The production 0.2.2 daemon on the 265U, with sessions working: **17.0% of a core mean and 52% at p95** over fifteen minutes, in 70 bursts.

**The budgets it breaks** ([budgets.md](../performance/budgets.md)): daemon CPU ≤ 2% of a core mean and ≤ 25% at p95; first launch ≤ 1 core in all.
The memory budget is **≤ 64 MiB `Private_Dirty`, "spent on caches that save CPU, not on a tight heap"**, so the cap is defending a number the budget no longer asks for: 0.2.2 settles at 13–18 MiB with it and 15–21 MiB without it.

## The fix

Raise or remove `DefaultMemoryLimit`, and stop calling `FreeOSMemory` after every rescan; the hook path's settle timer (item 16) can stay as the one place memory is handed back after a burst.
The comment on `DefaultMemoryLimit` cites a 20 MB target in `design/what-it-costs.md`; it becomes wrong with the fix and should cite the 64 MiB budget instead.
`pkg/daemon/daemon_test.go`'s `SetRelease` test pins the settle timer, not the per-rescan release, so it should survive.

Tests: a measure test whose limit is the budget, not today's figure — collections per minute of a daemon fed a steady stream of transcript changes, and `Private_Dirty` settled under 64 MiB.

Judge the fix with `perf-daemon-ab` against 0.1.7 and against today's build, settled and `--cold`, and write the numbers into a new report rather than editing these.
