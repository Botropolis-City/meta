# 303. The release runner fails the 600-district first-map bar, a wall-clock bar set for another machine

**Open, in progress since 2026-10-27 in the session "item 303". Filed 2026-10-27 (r1181), from 0.3.3's release dry run. Nobody's call — Aria ruled.**

0.3.3's release workflow dry run (40526462466) failed only `TestACityOfSixHundredDistricts/…/it_should_draw_its_first_frame_within_5_s`: *first frame after 7.000547493s*, on a shared GitHub runner (ubuntu-latest, no GPU, 4 vCPU).
Every other bar passed there, the 16 ms fitted frame at 15.4 ms among them; on Aria's machine, quietly, the first frame is 3.8 s (the performance manager's release check at `77ae413`).
The 5 s bar is wall-clock and was set for her machine (item 270).

Aria, 2026-10-27, asked how the release gate should treat it, chose **a separate CI bar**: the release runner holds the first map to its own limit, and her machine keeps 5 s.

## The fix

The test takes its first-map limit from where it runs: 5 s on the reference machine, and **9 s** on CI (`CI=true`, which the workflows set), the measured 7.0 s plus room for a shared runner's spread; it says in its log which limit it applied and why.
Nothing else in the test changes; CPU-a-frame and memory bars stay as they are everywhere.
Tests: the limit is 5 s without `CI` and 9 s with it; the log names the limit applied.
