# 176. The terminal table does not scroll: with more sessions than rows it loses its header and the cursor

**Open, in progress since 2026-10-20 in the session "item 176". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

`botropolis tui` renders every session as a line, pads to the terminal's height, and adds the footer (`(*program).View`, `botropolis/pkg/tui/program.go`).
Nothing limits the lines to the window.
When the view is taller than the terminal, Bubble Tea's renderer keeps its *last* `height` lines (`standard_renderer.go` in bubbletea v1.3.10: `newLines = newLines[len(newLines)-r.height:]`).
So the header goes first, then the top rows, and the cursor starts on the top row, out of sight.

The `metropolis` demo home has 19 live sessions and 28 with `a`.
In a 24-row terminal that leaves the column names and the first rows off the screen.
`j` walks the cursor down through rows that are not drawn, and `enter` attaches to a session the person cannot see.
The sidebar in the city had the same shape and was fixed as item 136.

The fix keeps a window of rows around the cursor, the header and the footer always shown, and says how many rows lie above and below.
`model_test.go` can pin it with more rows than a given height: the header is the first line, the cursor's row is among those drawn, and the line count is the height.
