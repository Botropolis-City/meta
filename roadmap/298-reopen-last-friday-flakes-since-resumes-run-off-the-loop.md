# 298. TestReopenLastFriday can count a resume two ticks late since resumes run beside the loop

**Open, in progress since 2026-10-27 in the session "item 298". Filed 2026-10-27 (r1164), from item 212's landing. Nobody's call — a flaky test.**

Item 212's first `make land` of slice 21 failed in `TestReopenLastFriday`: the resume was handed over in 2 ticks, where the test allows at most 1.
The test passed alone on the same rebased tree, and on the retry.
The commit beneath was item 286's (`26fe64a`), which moved Resume, New, Fork, Stop, Remove and Restore beside the city's loop, so a resume now completes on a goroutine and is seen by the loop on whichever tick follows; under load that can be the second.

## The fix

The test should wait on the resume's completion, through the settle seam item 286 gave the other render tests, not count ticks; or, if one tick is a promise the product makes, the hand-over must be made deterministic and the test kept.
Find which: read the test's intent and item 286's design, then fix the test or the code, red first by forcing the goroutine to finish a tick late.
