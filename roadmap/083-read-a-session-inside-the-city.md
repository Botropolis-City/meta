# 83. Read a session inside the city, and open a terminal only to reply

**Open, in progress since 2026-10-16 in the session "item 83". Filed 2026-10-15 (r412) from the planning session. Nobody's call — the design is settled; it waits on item 82's first slice, and Aria judges the frames.**

Depends on: 82 (slice 1)

What is being built: a pane inside the city's window that shows a session's last turns — your prompts, Claude's replies, and the question it is asking if it is waiting on you — so that checking on a session needs no terminal.
Only replying opens one.
The reasoning is in the private vision repository (`vision/command-center.md`), for sessions that have it checked out.

It is the second panel on [item 82](082-find-a-session-by-what-was-said-in-it.md)'s overlay stack, and it is how that stack is proved general:
whatever the finder needed that the pane does not stays the finder's, and whatever both need belongs to the stack.

## Rules it must keep

Item 82's — one window, nothing copied, nothing separate to run, no tokens, any desktop, no cgo — and two of its own:

- **Read when opened.**
  The pane reads the transcript when it opens and keeps nothing once it closes.
- **Typographic, for now.**
  Like the finder; illustration is for later panels.

## What exists to build on

- **The summary.**
  `i` toggles the selection's summary on the map (`scene.ToggleSummary`, `pkg/render/keys.go`), and the pane is the level below it.
- **The read.**
  `claude.Excerpt` (`pkg/claude/summary.go`) already reads the end of a session's conversation as plain text, for item 73's summaries.
  The pane needs the same read, kept as turns rather than flattened, and without `Summarise`, which spends tokens.
- **Replying.**
  `Enter` on the map attaches the selection through `pkg/control`, and the pane's reply is the same path.
- **Keys.**
  `o` is free on the map today; `r` is not, because it turns the camera.

## What it does

1. With a session selected, `o` — or a click on *read* in its summary — opens the pane over the dimmed city, and `Esc` closes it and puts the selection back.
2. It shows the last turns, newest at the bottom, with your prompts set apart from Claude's replies.
   Each tool call collapses to one line — the command or the path — and tool output is left out.
3. A session waiting on you leads with its question, word for word.
4. `PgUp` and `PgDn` scroll further back, and the pane never reads more than it shows.
5. `Enter` attaches, to reply.
6. A session whose transcript is gone says so, shows the prompts `history.jsonl` still has for it, and offers a new session in its directory.

## Done when

All six work on a live, a parked and a deleted session in the demo city, built test-first in the repository's style, `make lint` passes, and Aria has judged the frames.
