# 175. The terminal table cuts titles and lines by bytes, so a title with an accent or a dash can end in a broken character

**Open. Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

`botropolis tui` shortens text in three places, all by byte count (`botropolis/pkg/tui/model.go`):

- a title over 40 bytes becomes `title[:39] + "…"`;
- `clip` cuts the doing column and the project name with `s[:n-1]`;
- each line wider than the terminal becomes `line[:width]`.

A title, a folder or a tool description with any character outside ASCII — an accent, an em dash, curly quotes — can be cut inside that character, and the terminal shows a replacement mark.
And because the `…` added to every shortened title is three bytes, the width cut takes lines short of the terminal's edge.
Titles in a non-Latin script lose about two thirds of their room.

`fmt`'s `%-40s` pads by runes, which is why the columns line up anyway for ASCII.

The fix cuts by display width, not bytes; `lipgloss.Width`, which the TUI already imports, measures it, and `charmbracelet/x/ansi`'s `Truncate`, which lipgloss already brings in, cuts by it.
`model_test.go` can pin it with a title that has an em dash at byte 39 and assert the line is valid UTF-8.
