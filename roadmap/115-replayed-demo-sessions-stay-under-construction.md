# 115. A demo session replayed from a timeline stays washed out for the whole replay

**Open, in progress since 2026-10-18 in the session "item 115". Filed 2026-10-18 (r613) at Aria's request, from what item 109 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`210aa77`, r617).

A session whose timeline `botropolis/demo/scenarios/*.yaml` replays stays washed out, as if its building were still going up, for the whole replay.
The stager moves a replayed session's timestamps forward as it plays (`pkg/demo/stage.go`), so the city keeps reading it as a session that has only just arrived, and the construction-on-start state never ends.
Item 109 rendered its closing clips from staged homes without a timeline to work around it, which the release filming of `make demo-media` cannot do: every scenario with a replayed session would film this.

## The fix

Find which timestamp the city reads as "just arrived" — a session's first record, its start, or the file's creation time — and make the stager keep that one fixed while it advances the rest, so a replayed session arrives once and is built once.

Tests: a staged scenario that replays a session for longer than a build should show the building finished, not under construction, after the build time; mutated red on today's stager. Then one clip at true speed of a replayed scenario, for Aria.

## Answered while building

- **The filed cause did not reproduce** (item 115's session, 2026-10-18): a replayed session's build starts when its id first appears in a snapshot and ends 1.8 s later, whatever its timestamps. What washed out item 109's clips was a hover: with no cue showing the pointer, a recording fell back to the operating system's cursor, which xvfb parks at the middle of the screen, exactly where `pan_to` brings its district, so that district stayed hovered and the rest of the city receded for the whole clip.
- **The fix and its tree** (manager, 2026-10-18): during a recording or screenshot run, a pointer no cue has shown and no `--hover` has set hovers nothing; interactive use is unchanged, and no demo shot relied on the accidental hover. The item keeps its number, since it is the same symptom; the replayed-build test stays as a guard that was green from the start.

## What it turned out to be

The filed cause did not reproduce: the stager is not it.
A replayed session's building goes up once and finishes.
The city starts a build when a session first appears in a snapshot, not from any timestamp, so moving a replayed session's lines forward cannot keep it under construction.
A probe staged `buildings.yaml` through the director, played its timeline, and fed the city a snapshot every half second on one clock.
The replayed tidepool session arrived at 1 s, went up from 7.0 s to 8.5 s, and was finished from then on, as were kiln's and quillmark's.
A true-speed clip of `buildings/residential` filmed on r614 agreed: at 8 s the replayed tidepool building was still going up, and at 15.5 s it stood finished and in full colour.

What was washed out in that clip was every building outside tidepool, replayed or not, resting houses included.
A recording has no mouse, and until a cue shows the pointer or `--hover` parks one, the city read the system cursor, which xvfb leaves in the middle of the screen.
The shot's `pan_to: district:tidepool` brings its district to exactly that spot, so the district stayed hovered, its project card stayed up, and the hover highlight made the rest of the city recede for the whole clip.
`pan_to` itself never touches the pointer.

The fix: during a recording or a screenshot run, a pointer that no cue has shown and no `--hover` has set is over nothing (`210aa77`, r617).
Interactive use is unchanged, and the scroll wheel still zooms toward the same point it did.
No shot relied on that hover: the four `buildings` shots had it by accident, and `workshop/tour` and `metropolis/flyover` show the pointer with `point_at` before they pan.

Tests: `TestUnshownPointer` in `pkg/render/unshownpointer_test.go` was red on the code before the fix, and also checks that a `point_at` pointer still lights its district.
`TestReplayedSessionIsBuiltOnce` in `testing/integration/demo/stage_test.go` is the item's own test, that a replayed session is built after `SailFor` and `BuildFor`.
It was green from the start, since the stager was never the cause.
It stays as a guard, and a build that never ends turns it red.
