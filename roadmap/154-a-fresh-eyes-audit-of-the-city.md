# 154. Nobody has looked at the whole city since r96: a fresh-eyes audit for small defects

**Done 2026-10-20 (meta `4a3b065`, `52732d2` and `2f1ba13`, at r786). Filed 2026-10-19 (r777) at Aria's request, on the road to 1.0.0. Nobody's call — the audit finds; Aria judges what it files.**

The last audit of the whole app was [audit-r96](audit-r96.md), on 2026-09-18, about 680 revisions ago.
Since then the city gained a finder, a reading pane, groups, the journal, packing up, heft-sized buildings, the train on the map, the bridge and the statistics.
The open list is nearly empty, which says more about who is looking than about the city: item 151, cars driving backwards along x, was found by accident, by the session building item 147,
and item 74's night glow by someone filming the website.

Aria, 2026-10-19, agreed to *"address some old roadmap items/bug fixing like the night mode and similar small things"*, and asked for this item to find the small things.

## What to do

1. **Shoot everything.** `make demo-media`, then every scenario in `dist/demo/` (hamlet, metropolis, workday, workshop, timelapse, layers, buildings), by day and by night, at fit and closest zoom, from all four rotations where the scenario allows.
2. **Walk every panel and mode** headlessly: the finder, the reading pane, the sidebar, the docked card, every lens, explain mode, the depot, triage, settings, help, the TUI, `botropolis status`, and each command's `--help`.
3. **Read each frame against what it should say**, using `DESIGN.md`, `design/` and the closed items that built it: overlaps, clipping, wrong layering, a mover going the wrong way, a label on the wrong thing, text that is cut off or contradicts the map, a key that does nothing or does two things.
4. **File each defect as its own item**, small and specific, with the shot and pixel coordinates, the mechanism if it is cheap to find, and "Nobody's call — a defect".
   Gather anything that is a matter of taste instead of a defect under one heading in this item, for Aria.
5. **Close this item** with a table of what was looked at and what was filed, so the next audit knows where this one stopped.

## Out of scope

- **Performance and memory.** Aria is building a performance testing framework on another machine (2026-10-19), so this audit measures nothing and files no performance items.
- **Fixing.** The audit files; other sessions fix. A one-line fix found on the way still goes in its own item, so Aria sees the list before the city changes under it.
- **The website**, except where it shows the app's frames.

## For Aria

Any small annoyance from daily use that a frame cannot show: add it here, or tell the planning or roadmap session, and it is filed with the rest.

## What the audit did, and where it stopped

Filmed at r777–r786 through `make demo-media` in the sealed container, from generated copies of the seven scenarios holding stills only, plus three clips; the command line was run against a home staged with `botropolis-demo stage`.
Nothing in the city was changed.

| looked at | how | filed |
| --- | --- | --- |
| every scenario: buildings, hamlet, layers, metropolis, timelapse, workday, workshop | 13:00 and 23:00, four headings, fit and ten notches in: 112 stills | [169](169-the-city-opens-with-every-session-arriving.md), [170](170-the-minimap-spills-out-of-its-panel-after-a-turn.md), [179](179-group-lines-are-drawn-over-buildings.md) |
| the strip, the lens panels, the view key, all six lenses | stills on metropolis and workshop | [171](171-the-strip-says-1-need-you-and-1-prs.md), [180](180-the-lens-panels-wording-disagrees-with-the-strip.md), [181](181-small-polish-mcp-calls-f-and-0-model-ids-finder-rows.md) |
| finder, reading pane, card and details, triage, board, settings, reference, timeline, journal, stream, City Plan, labels off, New session, close up, quit, hidden, breakdown, explain, scrub, sidebar turned and at night | one still each, on metropolis and workshop | [172](172-the-key-reference-misses-u-and-rebound-keys.md), [173](173-new-session-names-a-session-by-its-id.md), [181](181-small-polish-mcp-calls-f-and-0-model-ids-finder-rows.md), [182](182-the-reading-pane-shows-markdown-raw.md) |
| the demo's own stills, against what they are titled | the lens each still's digit selects | [177](177-the-layers-stills-show-the-wrong-lenses.md) |
| movers | clips at 3 frames a second: workday's timeline at fit, metropolis zoomed on its road, metropolis's train loop; and hamlet's first ten seconds | [169](169-the-city-opens-with-every-session-arriving.md), [187](187-a-demo-clip-filmed-for-over-an-hour-loses-its-sessions.md) |
| every command's `--help`, `status` (`--all`, `--json`), `bar`, `find`, `doctor`, `events`, `shell-init`, `version`, the terminal table | run against the staged metropolis home; the table read from `pkg/tui`, since a terminal could not be driven headlessly | [174](174-the-status-bar-names-the-first-alphabetically.md), [175](175-the-terminal-table-cuts-text-by-bytes.md), [176](176-the-terminal-table-does-not-scroll.md); `--json`'s help is in [167](167-the-cli-has-spread-and-ships-no-man-pages.md) |
| `DESIGN.md` and `design/` against what the frames show | read | [178](178-the-design-docs-still-describe-nine-views.md) |

**Checked and fine:** trains run nose first; a merge sends the delivery truck from its building towards the bridge, with the ribbon over it; tugs come in at the sea mouth and run up the river; the first sightings' captions are a feature, not a stray hover.

**Where it stopped, for the next audit:**

- **Every still shows the live sessions mid-arrival.**
  Stills are taken three frames after the city opens,
  and item 169 sails every live session in, so in the 112 rotation and zoom stills their lots are bare or under scaffolding.
  Buildings were seen standing only in the clips.
  Refilm the stills once 169 is fixed; building-level defects were under-seen.
- **Cars and vans were not seen moving.**
  No demo scenario has a session crossing projects, so nothing drives the roads; their direction rests on items 151 and 153's tests.
- **A tug's heading** could not be read at fit, where it is about 35 pixels and looks the same from both ends.
- **The workday clip after 19 seconds** is unreliable, because of item 187.
- **Not filmed:** timelapse's and workday's clips at 30 frames a second, the docked card, clicking (stills cannot click), and any lens on a scenario other than metropolis, workshop and layers.
- **Night glow** was left to item 74, which was working on it.
- **Performance** was out of scope.

The matters of taste the audit gathered for Aria were filed at her request as items 179–182.
