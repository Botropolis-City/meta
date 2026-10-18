# 115. A demo session replayed from a timeline stays washed out for the whole replay

**Open. Filed 2026-10-18 (r613) at Aria's request, from what item 109 found. Nobody's call — a defect.**

A session whose timeline `botropolis/demo/scenarios/*.yaml` replays stays washed out, as if its building were still going up, for the whole replay.
The stager moves a replayed session's timestamps forward as it plays (`pkg/demo/stage.go`), so the city keeps reading it as a session that has only just arrived, and the construction-on-start state never ends.
Item 109 rendered its closing clips from staged homes without a timeline to work around it, which the release filming of `make demo-media` cannot do: every scenario with a replayed session would film this.

## The fix

Find which timestamp the city reads as "just arrived" — a session's first record, its start, or the file's creation time — and make the stager keep that one fixed while it advances the rest, so a replayed session arrives once and is built once.

Tests: a staged scenario that replays a session for longer than a build should show the building finished, not under construction, after the build time; mutated red on today's stager. Then one clip at true speed of a replayed scenario, for Aria.
