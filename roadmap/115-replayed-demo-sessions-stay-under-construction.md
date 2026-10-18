# 115. A demo session replayed from a timeline stays washed out for the whole replay

**Open, in progress since 2026-10-18 in the session "item 115". Filed 2026-10-18 (r613) at Aria's request, from what item 109 found. Nobody's call — a defect.**

A session whose timeline `botropolis/demo/scenarios/*.yaml` replays stays washed out, as if its building were still going up, for the whole replay.
The stager moves a replayed session's timestamps forward as it plays (`pkg/demo/stage.go`), so the city keeps reading it as a session that has only just arrived, and the construction-on-start state never ends.
Item 109 rendered its closing clips from staged homes without a timeline to work around it, which the release filming of `make demo-media` cannot do: every scenario with a replayed session would film this.

## The fix

Find which timestamp the city reads as "just arrived" — a session's first record, its start, or the file's creation time — and make the stager keep that one fixed while it advances the rest, so a replayed session arrives once and is built once.

Tests: a staged scenario that replays a session for longer than a build should show the building finished, not under construction, after the build time; mutated red on today's stager. Then one clip at true speed of a replayed scenario, for Aria.

## Answered while building

- **The filed cause did not reproduce** (item 115's session, 2026-10-18): a replayed session's build starts when its id first appears in a snapshot and ends 1.8 s later, whatever its timestamps. What washed out item 109's clips was a hover: with no cue showing the pointer, a recording fell back to the operating system's cursor, which xvfb parks at the middle of the screen, exactly where `pan_to` brings its district, so that district stayed hovered and the rest of the city receded for the whole clip.
- **The fix and its tree** (manager, 2026-10-18): during a recording or screenshot run, a pointer no cue has shown and no `--hover` has set hovers nothing; interactive use is unchanged, and no demo shot relied on the accidental hover. The item keeps its number, since it is the same symptom; the replayed-build test stays as a guard that was green from the start.
