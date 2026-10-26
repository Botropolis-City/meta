# 260. The frame's draw-count wobble test fails on a busy machine

**Open, in progress since 2026-10-26 in the session "item 260". Filed 2026-10-26 (r1083), seen by item 213's session while landing. Nobody's call — a flaky test.**

Depends on: nothing

`TestTheWorkAFrameTakes` (`botropolis/testing/acceptance/framework_test.go`) asserts, from [item 236](236-where-a-vehicle-stands-changes-a-frames-draw-count.md), that the draw count moves by no more than a small `wobble` between settled frames as vehicles move along their lanes (1 by day).
On 2026-10-26 item 213's first landing failed it with a spread of 10 against 1, at a load average of about 25; it passed on `main` and on the same tree straight after, and item 213's change is in the daemon, which the frame's draw count cannot see.
So something in a settled frame's draw count depends on the machine's load: a likely suspect is a frame drawn while the city was not yet settled (a late snapshot, a look baked a frame later, a vehicle spawned by a snapshot that arrived slowly), counted as settled because "settled" is decided by a count of frames or a time rather than by what the frame drew.

## The fix

Reproduce it beside a parallel `go test` of other packages (as item 225 did), log each counted frame's draw count with what changed in it, and find which frames carry the spread.
Then make "settled" mean what the test assumes — no snapshot, bake or spawn since — so load can lengthen the wait but not change the count, and keep the wobble limits as they are: a limit is the goal, never loosened to pass.

Tests: the test passes many times in a row beside a loaded machine and still fails when a real wobble is introduced (a vehicle drawn on its own batch).

## Answered while building

- **The cause** (item 260's session, 2026-10-26, reproduced deterministically): not a late snapshot but the first-sighting caption. The staged home has sighted nothing, so the city captions a kind every 8 s of its own clock; the record of settled frames started at 4 s and doubled only when short of 104 frames, which at 4 s it barely met, so one dropped frame under load made it record 8 s and cross a caption coming down, where the labels layer is drawn straight for a frame (spread 19–29, the 10 item 213 saw). Forced to 8 s it failed 5 of 5.
- **The fix** (manager, approved): a debug-build `BOTROPOLIS_FRAME_SIGHTED=all` so the test's cities draw no first-sighting captions (captions keep their own tests); the record starts at 8 s, so load can only add a doubling; a failing wobble case logs the frames off the common count; each ceiling is lowered to what the 8 s record measures (day 19), never raised, and the wobble limits stay.
