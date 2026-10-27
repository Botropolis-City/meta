# 298. TestReopenLastFriday can count a resume two ticks late since resumes run beside the loop

**Fixed 2026-10-27 (`7691a05`, r1176). Filed 2026-10-27 (r1164), from item 212's landing. Nobody's call — a flaky test.**

Item 212's first `make land` of slice 21 failed in `TestReopenLastFriday`: the resume was handed over in 2 ticks, where the test allows at most 1.
The test passed alone on the same rebased tree, and on the retry.
The commit beneath was item 286's (`26fe64a`), which moved Resume, New, Fork, Stop, Remove and Restore beside the city's loop, so a resume now completes on a goroutine and is seen by the loop on whichever tick follows; under load that can be the second.

## The fix

The test should wait on the resume's completion, through the settle seam item 286 gave the other render tests, not count ticks; or, if one tick is a promise the product makes, the hand-over must be made deterministic and the test kept.
Find which: read the test's intent and item 286's design, then fix the test or the code, red first by forcing the goroutine to finish a tick late.

## Closed

Fixed in `7691a05` (r1176), in the Drive, not the product: the one-tick promise holds.
`Game.act` hands a resume to `actBeside` on the input's own tick; only `actor.Do` runs on the goroutine.
But the Drive is the actor, and `Drive.Do` stamped the tick on which that goroutine ran, so under load a resume handed over on tick 1 was counted on tick 2.
`TestFindByThreeWords`, `TestAnswerAndComeBack` and `TestStartASessionAnywhere` count ticks the same way and shared the flake.

- Each `Drive.Tick` now waits for what it sent beside the loop, through item 286's `settle`, so an action is counted on the tick the city handed it over (`pkg/render/drive_test.go`: an actor held 100 ms counted 63 ticks before the fix and 1 after).
- The wait is bounded at 5 s, and the tick fails with *an action beside the loop did not finish* rather than hanging the suite (the manager's guard, in the same test file).
- The Drive test and the four acceptance tests that use `UntilActed` pass under `-race`.
  The race detector found no race even without the fix, since the goroutine's `clearStatus` and the loop share `g.mu`, so the defect was the miscount, not a data race.
