# 249. Acceptance captures fail under load at the 30-second open ceiling

**Open, in progress since 2026-10-25 in the session "item 249". Filed 2026-10-25 (r1032), seen by item 183's session while landing. Nobody's call — a defect in the tests.**

Depends on: nothing

While item 183 landed its slice 2 at a load average of about 55, four acceptance tests failed with "the history was not read within 30s, so no frame is taken from a partial read"; all four passed on a rerun under the landing lock, and `make land`'s gate then passed.
The message comes from `openCeiling` (`botropolis/pkg/render/openceiling.go`), a wall-clock constant of 30 s that a capture waits for the daemon to read its history (item 202).
On a loaded machine the read takes longer than the ceiling, so a test fails on the machine's load rather than on what it asserts: the same shape as [item 225](225-testthreadcpu-fails-under-load.md), which the testing rules forbid (no wall-clock assertions).

## The fix

1. Name the four tests: run the acceptance suite beside a parallel `go test` of other packages until the message appears, and list each.
2. Keep the ceiling for real captures, where it guards against filming a partial read, but let the harness that runs acceptance captures set it (an option or an environment variable read only by devtools builds) to a bound that fails loudly only when the read has stalled, not when it is slow: for instance, no progress in the read for 30 s rather than 30 s in total.
3. Test both: a capture whose read stalls still fails, naming the ceiling; a capture whose read is slow but advancing waits for it.

Tests: the two cases above in `pkg/render`, and the named acceptance tests passing under the same load that failed them.

## Answered while building

- **It is what keeps CI red** (manager, 2026-10-25, from item 95's session): `main`'s Linux CI has failed `test-lint` on every push since at least `e39a6ac`, in `TestTheLooksAFrameKeeps` and `TestTheStillLayerAFrameKeeps`, with "the history was not read within 30s"; item 212's landing met the same in `TestTheStillLayerAFrameKeeps` at a load of 45. Those are two of the tests step 1 names.
