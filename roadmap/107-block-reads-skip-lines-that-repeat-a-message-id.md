# 107. Everything read from a transcript's tool calls skips lines that repeat a message id

**Fixed 2026-10-17 (`ab18f79`, r580). Filed 2026-10-17 (r571), from what item 89 found. Nobody's call — a defect.**

Claude Code writes one API message's content blocks on separate transcript lines that share the message's id.
`applyAssistant` in `botropolis/pkg/claude/transcript.go` returns early on a message id it has already seen, so its usage is counted once, and its loop over the message's blocks comes after that return, so every block on a repeat line is skipped.
In a demo session 7 of 10 tool calls sat on such lines; item 89 found it when its tool-call pulses stopped at 3 of 10, and fixed that one count (`3a3b20e`, r571) by counting tool calls before the return.

## What under-counts

Everything else read from the blocks, since before item 89:

- **Touches**, the files a session works on in other projects, which drive roads, cars and where a drone flies;
- **Messages** sent with SendMessage, which become team vans;
- **order lines**, and **pull-request actions** taken in tool calls.

## The fix

Dedupe the usage on a repeated message id and nothing else: read every line's blocks, and fold item 89's special case for tool calls back into the same loop.
It raises counts that existing tests and frames assume, so expect fixtures and expected values to move; each that moves is checked against a whole read, not simply updated.

Tests: data-driven over each block-level read — a message whose blocks are split across two lines sharing an id should count the block on the second line, and its usage once; mutated red on the current early return before it is trusted.
The scan's cost is measured before and after with `BenchmarkReadTranscript`, and item 91's load measure must not move beyond noise.

## Closed

Fixed in `ab18f79` (r580), with a changelog entry in `18b5bce`.
`applyAssistant` now reads every line's blocks in one loop, `applyBlock`, before the check for a message already seen, and item 89's tool-call count is part of that loop.
A tool call repeated on the next line is still read once, now for every block read and not only the count.
`botropolis/pkg/claude/transcript_split_test.go` covers each block read on the second of two lines sharing an id.
Its touch, message and two order cases failed on the early return.
Its usage, MCP and skill cases failed when the dedupe was removed,
and its repeated-call case failed when the repeat guard was removed.

**Two corrections to the list above, agreed with the manager.**
Pull-request actions were never under-counted: they are read in `apply()`, outside `applyAssistant`, so the return never reached them.
And the MCP and skill attributions are deduped with the usage, against "the usage and nothing else" read literally.
They belong to the message: measured over 60 recent transcripts in memory, both sat on a message's first line and repeated on every line of it, thinking and text included (MCP: 65 messages on 154 lines; skills: 546 on 1,193).
Counting them per line would have inflated both about 2.3 times, so the tests pin one per message.
Across the same transcripts, every assistant line held one block, and none of 11,452 lines repeating an id repeated a block.

**No fixture or expected value moved.**
The item expected some to.
A whole read of each of the demo corpus's 25 session transcripts was the same before and after: it has 132 lines that repeat an id, but none touches another project, sends a message or names an order.

**Cost.**
`BenchmarkReadTranscript`, run interleaved old and new to cancel machine load: medians 52.7 and 50.9 ms, the same bytes and allocations.
Item 91's `make bench`: every task took the same steps and ticks, and wall time stayed within noise.
