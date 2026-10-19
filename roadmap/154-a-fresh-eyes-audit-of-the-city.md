# 154. Nobody has looked at the whole city since r96: a fresh-eyes audit for small defects

**Open, in progress since 2026-10-19 in the session "item 154". Filed 2026-10-19 (r777) at Aria's request, on the road to 1.0.0. Nobody's call — the audit finds; Aria judges what it files.**

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
