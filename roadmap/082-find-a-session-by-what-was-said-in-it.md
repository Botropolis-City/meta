# 82. Find a session by what was said in it, from a panel inside the city

**Open, in progress since 2026-10-16 in the session "item 82". Filed 2026-10-15 (r412) from the planning session, as the first piece of work it settled. Nobody's call — the design is settled and slice 1's tests are agreed; Aria judges the frames.**

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

## Not in this item

Modes and qualifiers in the box (`repo:`, `branch:`, `is:waiting`), ranking that learns from what was picked, and moving settings, the timeline and the breakdown onto the overlay stack.
A tool that lets a Claude session query the finder is parked, because it would be a second thing to run.

## Done when

All five slices are in, `make lint` and the acceptance tests pass, and Aria has judged the frames.

## Sources

- [`exp/textinput` — Ebitengine v2.10.2 API](https://pkg.go.dev/github.com/hajimehoshi/ebiten/v2@v2.10.2/exp/textinput)
- [`RequestAttention` — Ebitengine v2.10.2 API](https://pkg.go.dev/github.com/hajimehoshi/ebiten/v2@v2.10.2#RequestAttention)
