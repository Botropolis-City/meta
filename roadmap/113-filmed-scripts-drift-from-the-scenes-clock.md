# 113. A filmed script's timing drifts from the scene's own clock

**Open, in progress since 2026-10-18 in the session "item 113". Filed 2026-10-18 (r597), from what item 106 found. Nobody's call — a defect.**

When a frame or clip is recorded under software GL, Ebitengine runs extra updates to hold 30 ticks a second, so the scene's clock — which counts ticks — runs ahead of the script player's clock, which counts recorded frames.
Item 106 measured the scene running about three times faster than its script: a burst of wheel events 0.12 s apart in script time was more than 0.35 s apart on the scene's clock, so the City Plan's debounce saw a slow scroll and opened mid-burst.
It tightened that one clip rather than touch the recorder, so anything timed in a filmed script — debounces, eases, transitions, liveliness — still drifts the same way.

## The fix

In record mode, tie the two clocks: either drive the script player from the scene's ticks, or allow exactly one update per recorded frame.
Whichever is chosen, a scripted pause of N seconds is N seconds on the scene's clock.

Tests: a recorded script that waits a known time and reads the scene's clock should see that time within one tick, under software GL; mutated red on today's recorder.

## Answered while building

- **The fix is one update per recorded frame** (item 109's session, 2026-10-18): with `--record`, the city's clock advances by update ticks, 30 a second, but a frame is written on each draw, and slow headless rendering makes Ebitengine run several updates per draw, so a 4.8 s job spanned about 1.6 s of a 10 fps clip. Clips ran about three times fast, and Aria judged several speeds from them — the build, the hoist and the compaction trucks — so once this lands they are re-judged from true-speed clips (Aria, 2026-10-18).
- **The test tree** (manager, 2026-10-18): approved after one round — while recording, one update per drawn tick (an update waits until the last one is drawn, a draw with no update counts nothing, and Ebitengine's TPS is synced to frames), with a frame written every 30/fps draws as today, so a written frame at 10 fps is exactly 0.1 s of the city's clock; the acceptance test records 3 s at 10 fps under software GL and expects 30 frames and 3 s within a tick, run red on the old recorder first.
