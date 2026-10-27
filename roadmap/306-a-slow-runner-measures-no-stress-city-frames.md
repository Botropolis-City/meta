# 306. On a slow runner the stress city measures no frames, and that check still fails the release

**Fixed 2026-10-27 (`56796db`, r1185). Filed 2026-10-27 (r1184), from 0.3.3's release run 40544660300. Nobody's call — it follows Aria's ruling in item 305.**

0.3.3's release run reached its performance job with item 305's report mode working: *"over its bar, reported and not gated: fitted took 19.49ms"* and *"first frame after 19.30s, the limit 9s"*.
But the runner was so slow that the city drew no frame inside its measuring window, so `it_should_report_its_frames,_or_nothing_was_measured` (`bigcity_test.go:240`, *Should NOT be empty*) failed the job, and nothing was tagged.

That check guards against a measurement that silently measured nothing; on the reference machine it must keep failing.
On a shared runner, under Aria's ruling that the stress city reports there and gates on the reference machine (item 305), it reports too: *"no frames measured: the runner drew none within the window"*, and passes.

## The fix

Send the frames-measured check through item 305's `holdToBar` like the bars, so it gates without `CI` and reports with it.
Tests: without `CI`, no frames measured fails; with `CI`, it is logged and passes.

## Closed

`holdToFrames` in `testing/acceptance/bigcity_test.go` (`56796db`, r1185) sends `it should report its frames, or nothing was measured` through item 305's gate, beside `holdToBar`, through one shared `hold`.
Without `CI` a measurement with no frames fails as before; with `CI` set it is logged and passes.
The logged line takes the bars' shape, *no frames measured, reported and not gated: the runner drew none within the window*, rather than the item's quote, so every reported measure reads alike — flagged for Aria.
`TestTheStressCityGate` covers both modes with its fake `t`, for no frames and for frames; it was red against a stub first.
The stress tests themselves were not rerun locally, since the call site changed by one line and item 305 had proven the report mode; `make land` passed its gate.
CI run 40546815600 on `56796db` was green.
The report mode on a slow runner is proven only when 0.3.3's next release run reaches the performance job.
