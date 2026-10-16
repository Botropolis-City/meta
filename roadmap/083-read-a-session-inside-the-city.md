# 83. Read a session inside the city, and open a terminal only to reply

**Done 2026-10-16 (`08ec60b`, r456). Filed 2026-10-15 (r412) from the planning session.**

Depends on: 82 (slice 1)
Landed: slice 1 (`095cda2`, r435).
Landed: slice 2 (`f2cfb87`, r442).
Landed: slice 3 (`90589a9`, r446).

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

## Slices and their tests

Agreed with Aria on 2026-10-16, before any were written.
Each slice is built test-first in the repository's *when / and / it should* style, passes `make lint`, and lands with a frame of a synthetic home for Aria to judge.

```
── Slice 1: the read ─────────────────────────────────────────────
pkg/claude · ReadConversation(path, skip, count)
  when a transcript has typed prompts and replies
    it should keep them oldest first, each marked yours or Claude's
  when a user record is a tool result                → it should leave it out
  when a user record is the CLI's own (isMeta, isCompactSummary, "<…")
                                                     → it should leave it out
  when a record is a subagent's (isSidechain)        → it should leave it out
  when one reply is written as several records of one message
                                                     → it should keep it as one turn
  when Claude runs a command                         → it should keep one line holding the command
  when Claude reads, edits or writes a file          → it should keep one line holding the path, not the content
  when Claude calls any other tool                   → it should keep one line naming the tool
  when a line does not parse                         → it should skip it and keep reading
  when the session is waiting on AskUserQuestion
    it should carry the question word for word
    it should carry its options
    and the question has been answered               → it should carry no question
  when a page is asked for, skipping the newest n
    it should return the count turns before them
  when more turns are asked for than the transcript holds
    it should return what there is
    it should say it reached the start
  when the transcript holds far more than the page   → it should read less of the file than the whole

── Slice 2: the pane ─────────────────────────────────────────────
pkg/city · the summary's actions
  when the summary is open                           → it should offer read

pkg/ui · LayoutReader
  when laid out in a 1280×800 window
    it should centre the panel across the window
    it should draw with the plates' palette, radius and grid
    it should name its keys: PgUp PgDn, enter to reply, esc to close
  when the window is narrower than the panel         → it should stay inside the window
  when there are turns
    it should put the newest at the bottom
    it should set your prompts apart from Claude's replies
    it should give each tool call one line
    it should wrap a long reply inside the panel
  when there are more lines than fit                 → it should drop the oldest and keep the newest
  when the session is waiting on a question
    it should lead with the question, above the turns
    it should list its options beneath it
  when the start of the conversation is shown        → it should say so at the top

pkg/render · the reading pane
  when a session is selected and o is pressed
    it should open the pane
    it should read that session's transcript
  when nothing is selected and o is pressed          → it should say to select a building first
  when the summary's read is clicked                 → it should open the pane
  when the pane is open
    and a key the map binds is pressed (t, x, s, Tab) → it should not reach the map
    and Esc is pressed
      it should close the pane
      it should keep the selection
    and the pointer clicks outside the panel         → it should close the pane
    and PgUp is pressed                              → it should read the page before
    and PgDn is pressed after PgUp                   → it should come back a page
    and PgDn is pressed at the newest                → it should stay
    and PgUp is pressed at the start                 → it should stay
    and Enter is pressed
      it should close the pane
      it should attach a live session, or resume a parked one
  when the pane closes                               → it should keep nothing it read
  when the read fails                                → it should say why in the pane

── Slice 3: a transcript that is gone ────────────────────────────
pkg/ui · LayoutReader
  when the transcript is gone
    it should say the conversation has been deleted
    it should show the kept prompts as yours
    it should name enter as a new session here

pkg/render · the reading pane
  when the selection's transcript is gone
    it should show the prompts history.jsonl has for it
    and Enter is pressed                             → it should start a new session in its directory
  when history.jsonl has nothing for it              → it should say no prompts were kept
```

### Added while building

Slice 1 kept two cases nobody had named: two replies that are messages of their own stay two turns, and a page further back than one 64 KB read reaches comes out whole across the boundary.

**Approvals lead too (Aria, 2026-10-16).**
A session paused on a permission prompt asks no question in its transcript: it has written the tool call, word for word, and no result for it yet.
The transcript alone cannot tell that from a command still running, so the pane leads with the pending call only when the session's state says it needs you, which the `Notification` hook sets, carrying its message as the session's note.
A session without hooks still reads as working while it waits on an approval, the same blind spot the map has.

```
pkg/claude · ReadConversation                       (slice 1, landed)
  when Claude's last tool call has no result yet, as while it waits on your approval
    it should carry the call as pending, word for word
    and the call has its result                      → it should carry nothing pending
    and the pending call is a question               → it should carry it as a question and not as a pending call

pkg/ui · LayoutReader                                (slice 2)
  when the session is waiting on your approval
    it should lead with the call it is asking to run, word for word
    it should carry the hook's note beneath it, when there is one

pkg/render · the reading pane                        (slice 2)
  when the session needs you and a call is pending   → it should lead with the approval
  when the session is working and a call is pending  → it should not lead with it
```

**Slice 2, as built.**
Item 88 landed between the tree and the code and folded the summary into the card's face, so there is no summary to open.
*Read* is on the card of every session whose transcript is Claude Code's, beside *generate summary*, and the test that the summary offers it now reads "when the selected session has a recap, it should offer read".
Two cases were added: the layout says how many turns it showed, which is how far PgUp goes, and it keeps every line between the title and the keys.
The pane's fill is opaque, because the selected card showed through the plates' translucency in the first frame.
Frame: `r442-item-83-reading-pane.png`, a live session asking a question, from a synthetic home; replaced at r447 (below).

**Slice 3, as built.**
A deleted transcript is told from an unreadable one by a sentinel error, and only then is `history.jsonl` read, through `claude.ReadPromptHistory`.
The deleted and parked frames were reached through the finder and `Ctrl+M`, since a session the map shows can be selected that way.

**The gap, closed** (`6b04629`, r447).
Turns that do not fill the pane now start directly under what leads it, which a test pins, and the three frames were re-rendered and replace the earlier ones:
`botropolis/docs/screenshots/r447-item-83-live.png`, `r447-item-83-parked.png` and `r447-item-83-deleted.png`.

## Answered while building

- **Slice 2's frame** (`r442-item-83-reading-pane.png`): one change, and otherwise it stands — close the gap, so the conversation flows straight under the question rather than being pinned to the bottom of the pane. Aria, 2026-10-16.
- **Slice 3's frames and the closed gap** (`r447-item-83-live.png`, `-parked.png`, `-deleted.png`): passed, with one addition — *"we should add a copy button next to each prompt"* on the deleted-transcript pane, built in this item before it closes. Aria, 2026-10-16.

## Closed

Done in three slices, a fix and an addition, all in botropolis: the read (`095cda2`, r435), the pane (`f2cfb87`, r442), a transcript that is gone (`90589a9`, r446), the gap closed (`6b04629`, r447), and a copy button beside each kept prompt (`08ec60b`, r456).
All six things the item asks for work on a live, a parked and a deleted session, which `r447-item-83-live.png`, `r447-item-83-parked.png` and `r447-item-83-deleted.png` show, and Aria passed them on 2026-10-16.
The copy buttons' frame, `botropolis/docs/screenshots/r456-item-83-copy.png`, went to her after closing, as the manager arranged; any change she asks for comes back as new work.

Two departures from the item as filed, both settled while building:

- **Read is on the card, not in the summary**, because item 88 folded the summary into the card's face while this item was in flight.
- **Approvals lead the pane as questions do** (Aria's request): a session that needs you leads with the tool call it is waiting to run, word for word, and the hook's note. A session without hooks still reads as working while it waits on an approval, as it does on the map.
