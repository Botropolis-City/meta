# 141. A live session's transcript is re-read whole every time it changes

**Fixed 2026-10-19 (`e51b6da`, r747). Filed 2026-10-19 (r711), from item 138's measurements. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`48fda48`, r746).
Landed: slice 2 (`e51b6da`, r747).

Item 138 measured the daemon on Aria's machine (`~/.claude`, 2.1 GB) and found a standing cost under the backfill it was fixing: when a live session's transcript changes, the loader re-reads that transcript from the start (`botropolis/pkg/state/loader.go:332`).
The roadmap manager's own session has a 339 MB transcript, and one rescan spent **3.7 s of CPU — 20 s of wall time on a contended machine** — re-reading it, on every write that session made.
It is there with statistics off too; long-lived sessions, which are exactly the ones a busy user keeps, make the city slower the longer they live.

## The fix

Read a live transcript incrementally: keep, per transcript, the byte offset and the running state the loader derives from it (turn, usage totals, tool calls, the tail it classifies), and on a change read only what was appended; fall back to a whole read when the file shrank, was replaced (inode or size below the offset), or its head changed.
Item 110 already resumes from a stored offset for statistics (`read_to`); this is the same idea for the live model.

Tests: an appended line should be read without re-reading the head (count bytes read through `measure`); a truncated or replaced file should be read whole; the incremental and whole reads should derive the same session; a measure test on a large synthetic transcript whose limit is "bytes read per append ≈ bytes appended".

## Fixed

Each live transcript now keeps a `claude.TranscriptReader` (`botropolis/pkg/claude/incremental.go`): the scan's running state and the end of the last line it applied, so a change reads only what was appended.
It reads the file whole again when the file is not the one it read, is shorter than it was, has a different first 4 KB, or no longer has a line's end where it stopped.
A torn last line is counted malformed, as a whole read counts it, and read again once finished.
A complete last line without its newline is applied, and anything but a newline after it reads the file whole.
A line over the cap halts the reader where it halts a whole read.
Each result is a copy without the scan's seen-message set, because the daemon serves the last snapshot while the next load runs.
Slice 2 does the same for a live session's subagents (`claude.SubagentReader`).

A one-line append to a 16 MB transcript made the load read 16.7 MB; it now reads 4,352 bytes (`botropolis/testing/acceptance/livetranscript_test.go`).
`TestTranscriptReaderEquivalence` and `TestSubagentReader` grow transcripts of every line kind four ways — line by line, in chunks that cut lines, a byte at a time, at once — and hold the reader equal to a whole read after every append.
Every guard in the reader was removed in turn and a test failed each time.
Two failed only once byte counts were asserted, because the fallback still gave the right answer by reading whole.
That pass found one bug: after halting at a too-long line, a file cut back to just past the offset kept the stale result, so the guard is "no shorter than the last read", not "no shorter than the offset".
Changelog: under *Fixed*, `450a087`.

**Memory, accepted as is** (manager, 2026-10-19): the kept scan costs about 76 bytes per distinct message id, its seen-id set.
On 64 MB synthetic transcripts that was 1.5 MB with ~3 KB lines and 12 MB with tiny lines, the worst case.
A 339 MB live transcript with realistic lines is estimated at about 8 MB, against the ~1 MB a scan otherwise leaves resident.
An append's cost does not grow with it: `TestTranscriptReaderAppendCost` holds a hundred-times-longer transcript to the short one's allocations, and fails if the set is copied.
If it is ever wanted, the set could keep only recent ids, provided a message's repeated lines always arrive close together.
That changes what a whole read derives too, so it would need evidence from real transcripts and its own item.
