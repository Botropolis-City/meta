# 208. The daemon keeps its start-up memory peak until a hook event fires

**Fixed 2026-10-23 (`07e282e`, r928). Filed 2026-10-22 (r917), from item 198's close. Nobody's call — the budget is set (daemon ≤ 64 MiB of `Private_Dirty`, settled).**

Depends on: nothing

[Item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md)'s acceptance test, a daemon settled on the synthetic home plus 2,000 small sessions, passes its `Private_Dirty` gate at **59–63 MiB against 64**: too tight for a gate every landing runs.
Most of it is not grouping: the daemon keeps its start-up peak, because it only returns freed memory to the OS after a hook event (the settle-timer release [item 157](157-the-daemon-s-heap-cap-keeps-it-collecting.md) kept). A daemon that loads and then sees no hook holds its peak indefinitely.
[Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) is cutting what each rescan allocates, which lowers the steady part, but only a release returns the start-up peak.

## The fix

Release freed memory to the OS once the first load has settled (and after any burst of rescans goes quiet, on the same settle timer), not only after hook events. Measure it: what it costs in CPU, and what `Private_Dirty` settles at.

Tests: a daemon that loads a large home and then sees no hook event settles under the budget with margin (report the margin); the release does not run during a burst of rescans (item 157's lesson: releasing per rescan cost most of a core).

## Closed

`Daemon.Rescan` now arms the settle timer that hook events arm, so the daemon returns freed memory once loading has been quiet for 5 s (`SettleAfter`), with or without a hook.
Every rescan re-arms it, so a burst releases once, after it ends, never per rescan; and it never waits more than a minute (`ReleaseCeiling`) from the first activity since the last release, so a daemon kept busy by a writing session, which rescans every second and never settles, still releases once a minute (the ceiling was the roadmap manager's addition).

`TestDaemonWithTwoThousandSessions` now waits for the release, a forced collection in the gctrace, before reading `Private_Dirty`, gates the 64 MiB budget and logs the margin every run, with no margin gate.
It settled at **42 MiB, 21 MiB under the budget**, against 59–61 before; with the `Rescan` call removed it fails, never releasing, at 61 MiB.
`pkg/daemon`'s tests pin the release after a first load with no hook, none during a burst of rescans and one after it, and at most one per ceiling under a steady stream.

What it costs in CPU: the stream tests did not move beyond noise, `TestDaemonUnderAStreamOfChanges` at 0.2% of a core and 2 collections a minute, and the settled stream at 1.1–1.2%.
Deviation, for Aria: the release's own CPU was not isolated. It is one forced collection a minute at most while busy, and the 2,000-session stream windows read 9.3% and 5.8% of a core against 7.3% and 5.7% before, on a machine other landings were loading.
