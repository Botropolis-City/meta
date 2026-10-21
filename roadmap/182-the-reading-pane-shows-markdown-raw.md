# 182. The reading pane shows Claude's Markdown as raw text

**Fixed 2026-10-20 (`a170852`, `fa3796f`, `8384611`, `9933c3a`, r826–r839). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154, from its matters of taste, at Aria's request. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`a170852`, r826).
Landed: slice 2 (`fa3796f`, r832).
Landed: slice 3 (`8384611`, r836).
Landed: slice 4 (`9933c3a`, r839).

The reading pane (`o`, or *read* on a card) shows a session's conversation without leaving the city.
Claude's replies are Markdown, and the pane prints them as typed: `**Step 1: refactor.**` with its asterisks, `` `to_html` `` with its backticks, and list markers as plain hyphens.

![The reading pane on a reply full of Markdown](../docs/references/182-the-reading-pane-shows-markdown-raw.png)

Shot: `metropolis`, keys `Tab O`, 1920×1080; the crop is (560, 90)–(1360, 990), the pane on *Ferrylight docs*.

The pane is laid out by `ui.ReaderPanel` and drawn by `(*reader).draw` (`botropolis/pkg/render/reader.go`), which wrap each line of text and set it in one face.
Nothing between the transcript and the pane reads Markdown.

What a fix could be, smallest first: strip the markup that only decorates (`**`, `__`, backticks around a word) so the prose reads cleanly; then bold and code faces for those spans, which the city does not ship yet; then lists and headings laid out as such.
Code blocks would want a monospace face too.
A test on the wrapping can hold a reply with `**bold**` and `` `code` `` to producing no asterisks or backticks in the laid-out lines.

**Decided with the manager, 2026-10-20.**
Replies are parsed with goldmark (`github.com/yuin/goldmark`, MIT), client-only, so `botropolisd`'s dependency graph is untouched.
The monospace face is Go Mono, from `golang.org/x/image/font/gofont/gomono` (BSD-3, Bigelow & Holmes), its licence beside it in `pkg/assets/fonts/` and its thanks in the README.
Bold comes from Inter's own weight axis; emphasis stays upright, because the variable file has no italic axis.
Beyond the item's own list, Claude writes these often enough to handle: GFM tables, laid out as a monospace block with aligned columns and clipped like code; blockquotes, as an indented block without the marker; a horizontal rule as a block of its own; raw HTML shown as text, never interpreted; and links showing their text, then the URL in parentheses when it differs.
Only Claude's replies are read as Markdown: your prompts and tool calls stay as typed.
Two slices: the first reads the Markdown and lays it out in the one face; the second draws bold and monospace.

## Closed

Fixed in four slices rather than the two planned.
Slice 1 reads Claude's replies with goldmark and lays them out without their markup; slice 2 sets bold from Inter's weight axis and code, code blocks and tables in Go Mono, puts a half-line between blocks but not between a list's items, and adds BSD-3-Clause to every package's licences; slice 3, at Aria's request after the first frame, puts code on a faint tint from the palette's hairline colour and sets a table's header row in Go Mono Bold; slice 4 undoes a cost the first three added.
The tests are `pkg/ui/markdown_test.go`, the Markdown cases in `pkg/ui/reader_test.go`, which hold each tint to exactly its own rows, and the style cases in `pkg/render/font_test.go`.

The frames, on the recorded Ferrylight reply with a table and a code block appended in a scratch copy of the corpus: [before and after](https://github.com/Botropolis-City/botropolis/blob/main/docs/screenshots/r832-item-182-reader-before-after.png) and [with the code tint](https://github.com/Botropolis-City/botropolis/blob/main/docs/screenshots/r835-item-182-reader-code-tint.png), which Aria approved on 2026-10-20.
The second is named r835, one short of the r836 slice 3 landed as, because another item landed during its gate.

**Cost.** The pane is laid out every frame it is open, and slices 1 to 3 ran goldmark over every visible reply each frame.
Slice 4 reads each reply once, off the frame, when its page is read, and makes the styled wrap measure each word once.
`BenchmarkLayoutReader` (`pkg/ui/reader_bench_test.go`), one frame over a page of 40 Markdown replies, on a loaded 14-core machine:

| | time a frame | garbage a frame | allocations |
| --- | --- | --- | --- |
| before item 182, plain wrapping | 0.19 ms | 21 KB | 222 |
| after slice 3 | 1.4–1.5 ms | 167 KB | 1957 |
| after slice 4 | 0.42–0.51 ms | 54 KB | 700 |

It reports and never gates.
What remains over the plain pane is the richer layout itself: more lines, runs and tints.

**For Aria.** Emphasis is upright, since Inter's variable file has no italic axis.
`TestStartUpPeak` failed one landing at 258 MB against its 240 MB limit; main measured the same 207–239 MB as this item's branch, and the numbers are in item 156.
