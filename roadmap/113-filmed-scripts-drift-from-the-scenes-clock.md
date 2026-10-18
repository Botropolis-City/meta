# 113. A filmed script's timing drifts from the scene's own clock

**Open. Filed 2026-10-18 (r597), from what item 106 found. Nobody's call — a defect.**

When a frame or clip is recorded under software GL, Ebitengine runs extra updates to hold 30 ticks a second, so the scene's clock — which counts ticks — runs ahead of the script player's clock, which counts recorded frames.
Item 106 measured the scene running about three times faster than its script: a burst of wheel events 0.12 s apart in script time was more than 0.35 s apart on the scene's clock, so the City Plan's debounce saw a slow scroll and opened mid-burst.
It tightened that one clip rather than touch the recorder, so anything timed in a filmed script — debounces, eases, transitions, liveliness — still drifts the same way.

## The fix

In record mode, tie the two clocks: either drive the script player from the scene's ticks, or allow exactly one update per recorded frame.
Whichever is chosen, a scripted pause of N seconds is N seconds on the scene's clock.

Tests: a recorded script that waits a known time and reads the scene's clock should see that time within one tick, under software GL; mutated red on today's recorder.
