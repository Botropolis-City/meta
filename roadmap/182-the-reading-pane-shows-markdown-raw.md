# 182. The reading pane shows Claude's Markdown as raw text

**Open, in progress since 2026-10-20 in the session "item 182". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154, from its matters of taste, at Aria's request. Nobody's call.**

Depends on: nothing

The reading pane (`o`, or *read* on a card) shows a session's conversation without leaving the city.
Claude's replies are Markdown, and the pane prints them as typed: `**Step 1: refactor.**` with its asterisks, `` `to_html` `` with its backticks, and list markers as plain hyphens.

![The reading pane on a reply full of Markdown](../docs/references/182-the-reading-pane-shows-markdown-raw.png)

Shot: `metropolis`, keys `Tab O`, 1920×1080; the crop is (560, 90)–(1360, 990), the pane on *Ferrylight docs*.

The pane is laid out by `ui.ReaderPanel` and drawn by `(*reader).draw` (`botropolis/pkg/render/reader.go`), which wrap each line of text and set it in one face.
Nothing between the transcript and the pane reads Markdown.

What a fix could be, smallest first: strip the markup that only decorates (`**`, `__`, backticks around a word) so the prose reads cleanly; then bold and code faces for those spans, which the city does not ship yet; then lists and headings laid out as such.
Code blocks would want a monospace face too.
A test on the wrapping can hold a reply with `**bold**` and `` `code` `` to producing no asterisks or backticks in the laid-out lines.
