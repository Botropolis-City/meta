# 82. Find a session by what was said in it, from a panel inside the city

**Done 2026-10-16 (`e0bfe60`, r444). Filed 2026-10-15 (r412) from the planning session, as the first piece of work it settled.**

Depends on: nothing
Landed: slice 1 (`86de907`, r414).
Landed: slice 2 (`764e9b5`, r418).
Landed: slice 3 (`1e1b1b0`, r423).
Landed: slice 4 (`9bf8576`, r433).
Landed: slice 5 (`4227a42`, r443).

What is being built: a finder that searches every session on the machine by what was said in it — your prompts first, then Claude's replies, its recaps, and the commands and paths it touched — opened as a panel inside the city's window.
The reasoning behind it is in the private vision repository (`vision/find.md`), for sessions that have it checked out; this item is what to build.

It is also where the city gets a modal layer.
The finder is the first panel on it, and [item 83](083-read-a-session-inside-the-city.md)'s reading pane is the second.
[Item 84](084-a-global-shortcut-off-by-default.md), a global shortcut that is off by default, opens the finder from other applications.

## Rules it must keep

- **One window.**
  The finder is a panel drawn inside the city, never a window of its own.
- **Nothing is copied.**
  The index is held in memory and rebuilt from Claude Code's own files, and nothing derived from `~/.claude` is written to disk.
  A transcript Claude Code deletes leaves the index with it, and Claude Code's own settings, `cleanupPeriodDays` among them, are read and never changed.
- **Nothing separate to run.**
  The daemon holds the index when it is running, and the city builds its own when it is not, the way `commands.Feed` already falls back from the daemon to polling.
  There is no helper process and no script.
- **No tokens.**
  Matching and counting only.
- **Any desktop.**
  Nothing assumes a window manager, and desktop-specific behaviour goes behind one seam with a fallback that works everywhere.
- **No cgo.**
  The build runs with `CGO_ENABLED=0` (`botropolis/Makefile`), and stays that way.
- **Typographic.**
  The panel is an overlay in the manner of the plates and cards in `pkg/ui` — the same type, grid, palette and radius — and carries no illustration.

## What exists to build on

- **Input modes.**
  `pkg/render/keys.go` runs a chain of flags — `settingsOpen`, `timeline`, `breakdown`, `searching`, and the quit prompt in `pkg/render/confirm.go` — each of which takes every key while it is set.
  The overlay stack replaces that chain for the finder.
  The others move onto it when they are next touched, not as part of this item.
- **The `/` box.**
  `pkg/render/search.go`: `searchKeys` reads `ebiten.AppendInputChars`, `drawSearch` lays a plate out with `ui.LayoutPlate`, `clickSearch` keeps the drawn plate's rectangle for clicks (bug 43), and `scene.SetFilter` dims what does not match.
  The finder replaces the box and keeps the filter.
  `pkg/city/filter_test.go` pins the filter, and nothing in `pkg/render` pins the box itself.
- **Keys.**
  Nothing on the map uses Ctrl today.
  `j`, `k` and `l` navigate inside the settings panel and the timeline, so the finder's `Ctrl+K` must not reach them.
- **Layout and theme.**
  `pkg/ui` lays panels out as pure functions tested on their own (`LayoutCard`, `LayoutPlate`), and its tests already read *"it should centre the panel"* and *"it should stay inside the window"*.
- **Text input.**
  Ebitengine v2.10.2's `exp/textinput` handles input methods on every desktop platform, and `AppendInputChars` does not.
- **Transcripts.**
  `pkg/claude` reads transcripts (`transcript.go`, and `Excerpt` in `summary.go`), but nothing reads `~/.claude/history.jsonl` yet.
  That file has to be read line by line, skipping any line that does not parse: one seen in the wild begins with NUL bytes.
- **The socket.**
  `pkg/proto` carries `snapshot`, `subscribe`, `event` and `events`, and a query is one more op.
- **Opening a session.**
  `pkg/control` opens terminals through `BOTROPOLIS_TERMINAL`, a command prefix, or else the first known terminal on the path, and the settings panel can set it (`config.KeyTerminal`).
- **The clipboard.**
  Ebitengine has no public clipboard API — its X11 and Win32 clipboard code is internal — so copying goes through `pkg/control`'s desktop seam the way terminals do.
- **The window.**
  `pkg/render/run.go` sets the X11 instance name `botropolis`, so desktop rules can match it.
  Ebitengine exposes no native window handle and no call that raises a window; it has `RequestAttention`.

## Slices

Each slice is built test-first, in the repository's *when / and / it should* style with testify, passes `make lint`, and lands with a frame of the demo city in `botropolis/docs/screenshots/` for Aria to judge.
Commits cite item 82.

1. **The overlay stack, with today's filter in it.**
   `Ctrl+K` (`⌘K` on macOS) or `/` opens a typographic panel over a dimmed city, and typing filters the map as `/` does today.
   `Esc` closes it and clears the filter.
   `Enter` closes it and keeps the filter, until slice 4 gives Enter its job.
2. **The index.**
   A package that both the daemon and the city host, a `find` op on the socket, and `botropolis find -n 5 "words"`, which prints matching sessions with or without the daemon running.
   It indexes your prompts (from transcripts and from `history.jsonl`), Claude's replies, recaps, and commands and file paths.
   Tool output stays out of the index, and a flag searches it straight from the transcripts.
   Ranking: field weight (your prompts, then recaps, then replies, then commands and paths, then titles), then recency, with live and waiting sessions first.
3. **Results in the panel.**
   One row per session, headed by your own words — the prompt that matched, or the first one — and never by the generated title, with its directory, its branch when it has one, and its age beneath.
   The matching passage is highlighted, `↑` and `↓` move, and a preview shows the session's last recap and its next step.
   A session whose transcript is gone still appears, found by its prompts, and says that its conversation has been deleted.
4. **Acting on a result.**
   `Enter` opens it through `pkg/control`: `claude attach` for a live session, and `claude --resume` in its own directory for a stopped one.
   For a session whose transcript is gone it offers a new session in the same directory instead.
   `Ctrl+Y` copies `cd <dir> && claude --resume <id>`, and `Ctrl+M` closes the panel and shows the session on the map.
5. **One city, and `botropolis find`.**
   The city listens on a small socket of its own, so a second `botropolis city` brings the first forward instead of opening another window.
   `botropolis find` opens the finder in the running city, or starts the city with it open.
   Bringing the window forward goes behind the seam that item 84 fills in; until a platform has it, the finder opens and the window asks for attention.
   The help text shows how to bind `botropolis find` in a desktop's own keyboard settings: GNOME's or KDE's custom shortcuts, a macOS keyboard shortcut, or a line in i3's config such as `bindsym $mod+k [instance="botropolis"] focus; exec --no-startup-id botropolis find`.

## Slice 1's tests

Agreed with Aria on 2026-10-15, before any were written:

```
pkg/ui · LayoutFinder
  when the finder is laid out in a 1280×800 window
    it should centre the panel across the window
    it should hang the panel from the top third, like a command palette
    it should put the field on the panel's first line
    it should draw with the plates' palette, radius and grid
  when the window is narrower than the panel
    it should stay inside the window
  when the query is wider than the field
    it should keep the caret in view

pkg/render · the overlay stack
  when nothing is open
    and Ctrl+K is pressed
      it should open the finder
    and / is pressed
      it should open the finder
  when the finder is open
    and a key the map binds is pressed (t, x, s, Tab)
      it should not reach the map
    and a character is typed
      it should filter the map behind the panel, as / does today
    and Esc is pressed
      it should close the finder
      it should clear the filter
    and Enter is pressed
      it should close the finder and keep the filter    (until slice 4)
    and the pointer clicks outside the panel
      it should close the finder
  when the quit prompt is armed and the finder opens
    it should stand the quit prompt down

pkg/render · the field
  when characters are typed
    it should insert them at the caret
  when Backspace is pressed
    it should delete the rune before the caret
  when an input method is composing
    it should draw the composition without filtering on it
```

## Slice 2's tests

Agreed with Aria on 2026-10-16, before any were written, with matching per passage: every word of a query must appear in one prompt, reply, recap, command, path or title.

```
pkg/claude · ReadSaid
  when a transcript has a typed prompt            → it should keep it as a prompt
  when a user record is a tool result             → it should leave it out
  when a user record is the CLI's own (isMeta, or "<…")  → it should leave it out
  when Claude replies with text                   → it should keep it as a reply
  when Claude runs a command                      → it should keep the command
  when Claude reads, edits or writes a file       → it should keep the path and not the content
  when the session left a recap                   → it should keep the recap
  when the session has a title                    → it should keep the title
  when a record is a subagent's (isSidechain)     → it should leave it out
  when a line does not parse                      → it should skip it and keep reading

pkg/claude · ReadHistory
  when history.jsonl holds prompts for two sessions
    it should key each prompt by its session
    it should keep each prompt's directory and time
  when a line begins with NUL bytes               → it should skip it and keep reading

pkg/find · Index
  when a transcript is indexed
    and every word of the query is in one passage → it should find the session
    and the words are only spread across passages → it should not find it
    and the query differs in case                 → it should find the session
  when only tool output holds the words           → it should not find the session
    and the tool-output search is asked for       → it should find it from the transcript
  when the transcript is gone and history.jsonl holds its prompts
    it should find it by its prompts
    it should say its transcript is gone
  when a transcript is deleted after indexing, and the index is refreshed
    it should drop what only that transcript said
  when a transcript grows after indexing, and the index is refreshed
    it should find what was added
  when the index is refreshed                     → it should write nothing under the home
  when sessions match in different fields (data-driven over each adjacent pair)
    it should rank prompt › recap › reply › command › title
  when two sessions match in the same field       → it should rank the more recent first
  when a live or waiting session matches in a weaker field → it should rank it above a stopped one
  when more sessions match than the limit         → it should return only the limit

pkg/daemon · the find op
  when a client sends find                        → it should answer with the index's hits

pkg/commands · Find
  when the daemon is listening                    → it should print what the daemon found
  when the daemon is not running                  → it should build its own index and print the same
  when nothing matches                            → it should say so

testing/acceptance · botropolis find
  when run with -n against a sample home and no daemon → it should print at most n matching sessions
```

As built, item 87 landed its own reader of `history.jsonl` first, `claude.ReadPromptHistory`, so the index reads through it and the NUL-byte case joined its tests rather than a second reader.
Two cases were added while building: a compaction summary is a user record that nobody typed, and is left out of prompts by its `isCompactSummary` mark; and a transcript's directory and branch are kept with what was said.

## Slice 3's tests

Agreed with Aria on 2026-10-16, before any were written, with the preview's next step being the session's last prompt.

```
pkg/ui · LayoutFinder, with results
  when there are results
    it should lay one row per session beneath the field
    it should head each row with the prompt that matched
    and the match was not in a prompt
      it should head the row with the session's first prompt, never its title
      it should show the matching passage beneath
    it should put the directory, branch and age beneath the head
    it should highlight each matched word where it is drawn
    it should mark the selected row
  when there are more rows than fit the window
    it should stop at the window's bottom and keep the selected row in view
  when a session's transcript is gone
    it should say its conversation has been deleted
  when a row is selected
    it should show a preview of its last recap and its next step

pkg/find · Hit
  when a session has a recap
    it should carry the recap with the hit

pkg/render · the finder's results
  when the query changes
    and typing pauses
      it should ask for results once
    and typing continues
      it should not ask yet
  when results arrive for a query that has since changed
    it should drop them
  when ↓ or ↑ is pressed
    it should move the selection, stopping at either end
  when the query is emptied
    it should clear the results
```

Two cases were added while building: the hit carries its last prompt as well as its recap, for the preview; and when the match lies past the row's width, the row shows the text around it, because the first frame had two rows whose match was clipped away.

The frame (`botropolis/docs/screenshots/r423-item-82-results.png`) shows something for Aria to rule on: while the finder is open, the map keeps slice 1's filter by title, project, branch, state or model, so a query the finder answers from what was said can leave the whole map dimmed ("4 sessions found, 0 of 5 on the map match").
Making the map follow the finder's results would answer it, and `Ctrl+M` in slice 4 is the natural place.

## Slice 4's tests

Agreed with Aria on 2026-10-16, before any were written, with the map following the finder's results rather than matching the words itself, as slice 3's frame suggested.

```
pkg/city · the finder's filter
  when the map is filtered to a set of sessions
    it should dim every building outside it
    it should count the ones inside it as matching
  when the set is cleared
    it should dim nothing

pkg/control · in a terminal, in a directory
  when a stopped session is resumed from the finder
    it should open a terminal in its directory running claude --resume <id>
  when a new session is started from the finder
    it should open a terminal in the directory running claude

pkg/commands · Actor
  when the action is to resume in a terminal   → it should resume there
  when the action is to start in a terminal    → it should start there
  when the action is to copy text              → it should copy the text

pkg/render · acting on a result
  when the finder has results
    and a character is typed             → it should dim the map to the sessions found   (replaces slice 1's)
    and Enter is pressed on a live session
      it should attach to it
      it should close the finder and keep the map dimmed to what was found
    and Enter is pressed on a stopped session → it should resume it in a terminal in its own directory
    and Enter is pressed on a session whose conversation is gone
      it should say Enter again starts a new session in its directory
      and Enter is pressed again          → it should start a new session there
    and Ctrl+Y is pressed
      it should copy cd <dir> && claude --resume <id>
      and the directory has a space in it → it should quote it
    and Ctrl+M is pressed
      it should close the finder
      it should select the session on the map
      and the session is not on the map   → it should say so
  when the finder has no results
    and Enter is pressed                  → it should close the finder and keep the filter   (as slice 1)
```

As built:

- The terminal runs `sh -c 'cd -- "$1" && exec claude --resume "$2"'` with the directory and id as arguments, because Terminal.app and terminals that hand windows to a server do not start where they were launched.
- Typing `m` or `y` without the modifier types it rather than acting, which mutation showed nothing pinned, so a case each was added.
- Until the finder's first results arrive, typing narrows the map by title, project, branch, state or model as `/` did; after that the map holds the last answer. That keeps item 91's reopen task, driven with no search behind it, as measured.
- The card's own resume (`claude --bg --resume` in the session's directory, then attach) is unchanged; the finder opens an interactive `claude --resume` in a terminal instead.

**The chords are settings** (Aria, 2026-10-16, landed at `9a15072`, r438).
On macOS slice 4 made show-on-map ⌘M, which minimizes the window before the city sees it.
`find_key`, `find_copy_key` and `find_show_key` take modifiers and a key such as `alt+s`, where `mod` is ⌘ on macOS and Ctrl elsewhere; the defaults are `mod+k`, `mod+y` and `ctrl+m`, and a chord macOS keeps (⌘M, ⌘H, ⌘Q, ⌘W) or a key the city cannot read is refused when the city starts.
Agreed tests:

```
pkg/config · ParseChord
  when a chord names modifiers and a key ("ctrl+m")   → it should read both
  when it uses mod (data-driven: darwin, linux)       → it should be ⌘ on macOS and Ctrl elsewhere
  when it names a key Ebitengine does not know        → it should refuse it, naming the setting
  when it is a chord macOS keeps (⌘M ⌘H ⌘Q ⌘W) on macOS → it should refuse it and say what macOS does with it
  when nothing is set (data-driven: darwin, linux)
    it should open the finder on mod+k, copy on mod+y and show on ctrl+m

pkg/render · the finder's chords
  when show is set to another chord (alt+s)
    and that chord is pressed → it should show the session on the map
    and Ctrl+M is pressed     → it should not
  when the help is drawn      → it should list the chords as configured
```

## Answered while building

- **Slice 5's test tree:** agreed as proposed: the city's own socket beside the daemon's, a second `botropolis city` bringing the first forward, `botropolis find` with and without words, a stale socket taken over, scripted cities neither listening nor deferring, and the binding help for GNOME, KDE, macOS and i3. The roadmap manager, 2026-10-16, from this item's slice 5 and its rules: one window, any desktop, no cgo.
- **What a second `botropolis city` prints:** "the city is already open; brought it forward" on stderr, and it exits 0, since bringing it forward is success. The roadmap manager, 2026-10-16, a CLI convention nothing here decides otherwise.

## Slice 5's tests

Approved by the roadmap manager on 2026-10-16, before any were written, with a second `botropolis city` printing "the city is already open; brought it forward" on stderr and exiting 0.

```
pkg/single · the one city's socket
  when no city is listening
    and a city starts                         → it should listen
  when a city is listening
    and a second city starts                  → it should ask the first to come forward and not open a window
    and botropolis find is run                → it should ask the first to open the finder
  when the socket was left by a city that died
    and a city starts                         → it should take it over
  when a city is scripted (screenshot, record, headless) → it should neither listen nor defer

pkg/render · requests from outside
  when a request to come forward arrives
    and the window is minimized               → it should restore it
    and the desktop cannot raise windows      → it should ask for attention
  when a request to find arrives              → it should open the finder and come forward

pkg/cli · find
  when run with no words and a city is running   → it should open the finder in that city
  when run with no words and no city is running  → it should start the city with the finder open
  when run with words                            → it should print matches, as in slice 2
  when its help is shown                         → it should show how to bind it in GNOME, KDE, macOS and i3

testing/acceptance · one city
  when a second botropolis city starts beside a running one → it should exit without opening a window
```

As built, the two cases about whether a city is running are tested in `pkg/commands` against a real listening city, and `pkg/cli` tests only that no words opens and words search.
With no city running, `botropolis find` replaces itself with `botropolis city` and the same arguments rather than starting the city from a command without the city's flags.
The window comes forward through a seam item 84 fills in; until then it is restored if minimized and asks for attention.

**The finder resumes as the card does** (Aria, 2026-10-16, landed at `e0bfe60`, r444).
Slice 4 had `Enter` open a terminal running a plain `claude --resume` through `sh`, so closing the terminal ended the session and a shell wrapper around `claude` was skipped.
`Enter` now sends the card's resume (`claude --bg --resume` in the session's folder, then attach), and a deleted conversation's second `Enter` the card's *new session here*; the terminal path is gone.

## Not in this item

Modes and qualifiers in the box (`repo:`, `branch:`, `is:waiting`), ranking that learns from what was picked, and moving settings, the timeline and the breakdown onto the overlay stack.
A tool that lets a Claude session query the finder is parked, because it would be a second thing to run.

## Done when

All five slices are in, `make lint` and the acceptance tests pass, and Aria has judged the frames.

Frames judged, in `botropolis/docs/screenshots/`:

- `r414-item-82-finder.png` (slice 1): passed by Aria, 2026-10-16.
- `r423-item-82-results.png` (slice 3): passed by Aria, 2026-10-16.
- `r433-item-82-show-on-map.png` (slice 4): passed by Aria, 2026-10-16.
- `r443-item-82-opened-by-find.png` (slice 5): with Aria.

## Closed

Done 2026-10-16, in five slices, each built to an agreed tree and each frame passed by Aria: the overlay stack and the finder panel (`86de907`, r414), the index and `botropolis find` (`764e9b5`, r418), results in the panel (`1e1b1b0`, r423), acting on a result (`9bf8576`, r433), and one city (`4227a42`, r443).
The finder is the first panel on the overlay stack, so item 83's reading pane has it to stand on, and slice 5's window seam is the one item 84 fills in.

Where it differs from what the item asked, each by Aria's ruling or recorded above:

- **Resuming matches the card** (`e0bfe60`, r444): the item asked for `claude --resume` in the session's own directory; `Enter` sends the card's resume instead, and a deleted conversation's second `Enter` the card's *new session here*.
- **The chords are settings** (`9a15072`, r438): `find_key`, `find_copy_key` and `find_show_key`, with show-on-map on Control+M everywhere, because ⌘M minimizes the window on macOS.
- **The map follows the finder**: once results arrive it dims every session the finder did not find; until the first arrive, typing narrows it by title as `/` did.
- **The index costs the daemon about 4 MB**: measured on this machine at 20.1 MB idle before any find and 24.2 MB after, against the 20 MB idle budget from the milestones. Aria chose not to worry about it for now.

Found and fixed on the way: botropolisd answered every find with "this daemon keeps no index" (`5287c63`), `make publishable` measured remote refs against a local `main` every worktree has stale (`d9a2f97`), and `make-fixtures` built samples that turned the integration suite red for every item session (`57fbe3e`, `04186ff`).

## Sources

- [`exp/textinput` — Ebitengine v2.10.2 API](https://pkg.go.dev/github.com/hajimehoshi/ebiten/v2@v2.10.2/exp/textinput)
- [`RequestAttention` — Ebitengine v2.10.2 API](https://pkg.go.dev/github.com/hajimehoshi/ebiten/v2@v2.10.2#RequestAttention)
