# 208. The daemon keeps its start-up memory peak until a hook event fires

**Open. Filed 2026-10-22 (r917), from item 198's close. Nobody's call — the budget is set (daemon ≤ 64 MiB of `Private_Dirty`, settled).**

Depends on: nothing

[Item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md)'s acceptance test, a daemon settled on the synthetic home plus 2,000 small sessions, passes its `Private_Dirty` gate at **59–63 MiB against 64**: too tight for a gate every landing runs.
Most of it is not grouping: the daemon keeps its start-up peak, because it only returns freed memory to the OS after a hook event (the settle-timer release [item 157](157-the-daemon-s-heap-cap-keeps-it-collecting.md) kept). A daemon that loads and then sees no hook holds its peak indefinitely.
[Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) is cutting what each rescan allocates, which lowers the steady part, but only a release returns the start-up peak.

## The fix

Release freed memory to the OS once the first load has settled (and after any burst of rescans goes quiet, on the same settle timer), not only after hook events. Measure it: what it costs in CPU, and what `Private_Dirty` settles at.

Tests: a daemon that loads a large home and then sees no hook event settles under the budget with margin (report the margin); the release does not run during a burst of rescans (item 157's lesson: releasing per rescan cost most of a core).
