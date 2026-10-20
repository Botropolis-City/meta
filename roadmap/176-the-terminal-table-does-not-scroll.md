# 176. The terminal table does not scroll: with more sessions than rows it loses its header and the cursor

**Fixed 2026-10-20 (`550f396`, r825). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

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

## Fixed

The model takes the terminal's height (`SetHeight`, from the program's `WindowSizeMsg`) and `Lines` draws only the rows that fit above the footer.
Its offset moves only as far as the cursor needs, so `j` and `k` do not re-centre the table, and it is clamped when sessions end so no blank lines sit below rows.
A line under the rows reads `↑ 6 above · ↓ 15 below`.
On a tiny terminal that line goes first, then the header, and the cursor's row always stays (the manager's ruling, 2026-10-20).
The program now styles the cursor row by its `> ` marker, because a row's index no longer matches its line once the table scrolls.
`pkg/tui/model_test.go` pins it with 28 rows in a height of 10: header first, the cursor's row drawn, height-1 lines, the counts, no scroll on stepping back, a shrinking height, rows disappearing, and heights of 3 and 2.
No frame: it is a terminal view, and the tests carry the claim.
