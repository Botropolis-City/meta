# 141. A live session's transcript is re-read whole every time it changes

**Open, in progress since 2026-10-19 in the session "item 141". Filed 2026-10-19 (r711), from item 138's measurements. Nobody's call — a defect.**

Depends on: nothing

Item 138 measured the daemon on Aria's machine (`~/.claude`, 2.1 GB) and found a standing cost under the backfill it was fixing: when a live session's transcript changes, the loader re-reads that transcript from the start (`botropolis/pkg/state/loader.go:332`).
The roadmap manager's own session has a 339 MB transcript, and one rescan spent **3.7 s of CPU — 20 s of wall time on a contended machine** — re-reading it, on every write that session made.
It is there with statistics off too; long-lived sessions, which are exactly the ones a busy user keeps, make the city slower the longer they live.

## The fix

Read a live transcript incrementally: keep, per transcript, the byte offset and the running state the loader derives from it (turn, usage totals, tool calls, the tail it classifies), and on a change read only what was appended; fall back to a whole read when the file shrank, was replaced (inode or size below the offset), or its head changed.
Item 110 already resumes from a stored offset for statistics (`read_to`); this is the same idea for the live model.

Tests: an appended line should be read without re-reading the head (count bytes read through `measure`); a truncated or replaced file should be read whole; the incremental and whole reads should derive the same session; a measure test on a large synthetic transcript whose limit is "bytes read per append ≈ bytes appended".
