# 303. The release runner fails the 600-district first-map bar, a wall-clock bar set for another machine

**Fixed 2026-10-27 (`4d4d656`, r1182). Filed 2026-10-27 (r1181), from 0.3.3's release dry run. Nobody's call — Aria ruled.**

0.3.3's release workflow dry run (40526462466) failed only `TestACityOfSixHundredDistricts/…/it_should_draw_its_first_frame_within_5_s`: *first frame after 7.000547493s*, on a shared GitHub runner (ubuntu-latest, no GPU, 4 vCPU).
Every other bar passed there, the 16 ms fitted frame at 15.4 ms among them; on Aria's machine, quietly, the first frame is 3.8 s (the performance manager's release check at `77ae413`).
The 5 s bar is wall-clock and was set for her machine (item 270).

Aria, 2026-10-27, asked how the release gate should treat it, chose **a separate CI bar**: the release runner holds the first map to its own limit, and her machine keeps 5 s.

## The fix

The test takes its first-map limit from where it runs: 5 s on the reference machine, and **9 s** on CI (`CI=true`, which the workflows set), the measured 7.0 s plus room for a shared runner's spread; it says in its log which limit it applied and why.
Nothing else in the test changes; CPU-a-frame and memory bars stay as they are everywhere.
Tests: the limit is 5 s without `CI` and 9 s with it; the log names the limit applied.

## Closed

`firstMapLimit` in `testing/acceptance/bigcity_test.go` (`4d4d656`, r1182) gives the 600-district city's first frame 5 s without `CI` and 9 s with it.
`TestACityOfSixHundredDistricts` logs the limit it applied and why, as `first-map limit: 5s, the reference machine's limit: CI is not set (item 270)`.
Nothing else in the test changed.
`TestTheFirstMapLimit` covers both limits and the reason naming each, red against a stub before the fix.
Locally the first frame was 3.9 s under the 5 s limit, and CI run 40531540535 on `783cd76` (r1183) was green.
`783cd76` gives the new test file the same `linux` build constraint as `bigcity_test.go`, because make land's macOS vet failed without it.
The checker applies any non-empty `CI`, the repository's existing convention, not only `CI=true`.
And the subtest's name now carries the limit it applied, *it should draw its first frame within 5s* or *within 9s*.
The 9 s limit is proven only when the release workflow runs the performance tier on its runner.
