# 107. Everything read from a transcript's tool calls skips lines that repeat a message id

**Open, in progress since 2026-10-17 in the session "item 107". Filed 2026-10-17 (r571), from what item 89 found. Nobody's call — a defect.**

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
