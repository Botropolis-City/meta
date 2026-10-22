# 157. The daemon's 16 MiB heap cap and a forced release after every rescan keep it collecting garbage

**Fixed 2026-10-21 (`be5360c`, r873). Filed 2026-10-19 (r780), from the 0.2.2 performance reports. Nobody's call — a defect against the daemon budgets.**

Depends on: nothing
Landed: slice 1 (`be5360c`, r873).

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

## Closed

`DefaultMemoryLimit` is now 256 MiB, the first-launch budget, with `GOMEMLIMIT` still overriding it, and its comment cites both budgets; `Daemon.Rescan` no longer calls `FreeOSMemory`, so the hook path's settle timer is the one place memory is handed back.
`TestDaemonUnderAStreamOfChanges` runs the daemon on a copy of the synthetic fixture with one session writing a line every 200 ms for 30 s, and gates its own CPU time at ≤ 2% of a core, collections at ≤ 30 a minute (0.1.7 made 19) and settled `Private_Dirty` under 64 MiB.
It went from 299 collections a minute and 2.7% of a core to 18 and 1.1%, at 21 MiB.
`TestMemoryLimit` holds the limit at or above 256 MiB unless `GOMEMLIMIT` is set.

[The report](../performance/reports/2026-10-21-ultra7-265u-igpu-item-157.md) judges it against r871: settled, collections went from 1,104 to 38 a minute and CPU from 23.8% to 7.6% of a core mean; cold, from 23,956 collections and 265 CPU-seconds to 509 and 73, with a peak of 114% of a core against 394%.
The collector is gone from the profile, but **the daemon budgets still do not hold**: what is left is the rescans' own work, which is [item 196](196-a-settled-daemon-bursts-to-several-cores-on-rescans.md) settled and [item 159](159-first-launch-takes-the-machine.md) at first launch, and both now start from this report's numbers.

Deviation: 0.1.7 could not be compared, because it times out at start-up on this machine's 3.2 GiB history, settled or cold.
