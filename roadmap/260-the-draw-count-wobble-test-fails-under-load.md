# 260. The frame's draw-count wobble test fails on a busy machine

**Fixed 2026-10-26 (`eb932f0`, r1087). Filed 2026-10-26 (r1083), seen by item 213's session while landing. Nobody's call — a flaky test.**

Depends on: nothing
Landed: slice 1 (`eb932f0`, r1087).

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

## Closed

Fixed in one slice (`eb932f0`, r1087).
It was not a late snapshot.
A recording advances its clock one tick a frame however busy the machine (item 113), so the test's 4-second record always held exactly its 104 settled frames, with none to spare.
When one went missing, the record doubled to 8 seconds,
and an 8-second record reaches the first-sighting caption coming down 6 seconds in, its labels layer drawn straight for a frame: 19 to 29 commands by day, 34 to 44 by night, with the render-target switches over too.
That is the failure item 213's landings saw.
Forced to 8 seconds, the old test failed every time (5 of 5); at 4 seconds it passed every time, beside loads of 20 to 65, only by having exactly enough frames.

The debug frame log now stamps each frame's tick, and `TestTheWorkAFrameTakes` records 5 seconds once and judges exactly ticks 18 to 121, the 104 frames it always judged, so load lengthens the wait and never the span.
Every city it runs starts with every kind sighted (`BOTROPOLIS_FRAME_SIGHTED=all`, `Scene.MarkSighted`), so no caption comes down on a timer in what it counts; a caption's cost belongs to its own tests.
A failed wobble case logs each off-count frame by tick.
No limit moved: 20 by day and 35 to 37 by night, as item 236 left them.

- **Loaded:** 10 of 10 whole-test runs in a row passed, each beside `go test -p 4 ./pkg/...`, at loads 12 to 65, reading 20 to 20 and 35 to 37 every time; a 16-second record judges the same span and passes.
- **Mutation:** every mover's sprites drawn through a colour matrix fails both wobble cases (day 24 to 28 against 1, night 39 to 43 against 2), naming the ticks; drawing only the traffic cars that way changed nothing, since none falls in a redrawn rectangle in this span.

**Deviation, flagged for Aria:** the approved plan first started the record at 8 seconds.
Measured, that could not hold without loosening a limit: past 4 seconds the metropolis's own movers reach 21 by day and 38 by night (night 34 to 38 over 8 seconds), over the ceilings of 20 and 37.
So the span was pinned instead, and that gap is filed as [item 261](261-past-four-seconds-the-metropolis-draws-over-its-ceilings.md).
No pinned-caption case was added: with every kind sighted, a caption is no longer in any city the test draws.
