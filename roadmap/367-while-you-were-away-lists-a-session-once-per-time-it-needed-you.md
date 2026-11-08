# 367. "While you were away" lists a session once for every time it needed you

**Fixed 2026-11-07 (`642d7154`, r1340). Filed 2026-11-07 (r1333) at Aria's request. Nobody's call — Aria said what she wants.**

Aria, 2026-11-07: *"the "while you were away" page duplicates items. Meaning if a session needed me 7 times while I was gone, I will get 7 entries of that session. We should de-duplicate on session"*.

## Where it stands

When the window regains focus, `watchFocus` in `botropolis/pkg/render/timeline.go` opens the timeline with `g.away = g.scene.Away(g.awaySince)`, titled "While you were away".
`Scene.Away` in `pkg/city/scene.go` (line 1406) returns `s.log.Since(since, events.NeedsYou, events.Error)`: every needs-you and error event since you left, newest first, one row each.
So a session that needed you seven times gets seven rows.
`TestScene`'s away case in `pkg/city/scene_test.go` (around line 822) holds today's list.

## What it wants

One row per session in the away list, ordered by each session's newest event, newest first.
The row is that session's newest event, and it says how many times the session needed you or failed while you were away, so the count is not lost.
An event with no session keeps its own row.
Jumping from a row selects its session, as today.
The full timeline (`Events`) is unchanged: only the away list collapses.

Tests in `pkg/city`: a session with seven needs-you events since you left gives one away row, carrying the count 7; two sessions give two rows, the most recent first; a session with a needs-you and an error gives one row, its newest; an event with no session keeps its row; and the timeline still lists every event.
A frame of the away list with a repeated session, for Aria.
It ships in [0.5.1](366-release-0-5-1.md).

## Answered while building

- **The design and test tree** (roadmap manager, 2026-11-07): approved. `events.Event` gains `Times`, which only away rows set. `Scene.Away` collapses to one row per session, and the journal's "since" strip keeps counting every event, through `Scene.AwayEvents`. A row that stands for several events ends "· 7 times".
  The tests are in `pkg/city` `TestSceneAway` and the timeline's words in `pkg/ui`.

## Closed

Fixed in `642d7154` (r1340): the away list is one row per session, its newest event, ending "· 7 times" when it stands for several; an event with no session keeps its row.
`TestSceneAway` in `pkg/city` and `TestLayoutTimeline` in `pkg/ui` hold it,
and the timeline and the journal's "since" strip still count every event.
The frame, for Aria, is `botropolis/docs/screenshots/r1340-item-367-away-list.png` (`51fddbd8`, r1341): one session that needed you seven times and another that failed once, as two rows.
A screenshot run has no focus to lose, so it was filmed from a throwaway hook in the city that handed it the events and opened the list; nothing of the hook landed.
