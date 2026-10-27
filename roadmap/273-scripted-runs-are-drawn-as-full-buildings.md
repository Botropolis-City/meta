# 273. Scripted, non-interactive runs are drawn as full buildings

**Done 2026-10-26 (`64ccc26`, r1149). Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — Aria ruled; she judged the stall frames: "Good, land them."**

Depends on: nothing
Landed: slice 1 (`a0df84b`, r1115).
Landed: slice 2 (`64ccc26`, r1149).

Of the transcripts on Aria's other laptop, 365 are scripted runs (`entrypoint` `sdk-cli`: `claude -p`, the Agent SDK, tools that drive Claude) and 145 interactive (`cli`).
`pkg/claude` parses `Entrypoint` (`transcript.go`, `sessions.go`) and nothing reads it, so each scripted run is a building like a session someone works in.

Aria, 2026-10-26, on whether they should be buildings: *"Hide by default, setting shows as you describe, but when show let's make them something lighter than our existing buildings. Maybe we make them a little cart or stand (like hot dog stand or little bazarr shop or similar)"*.

## The fix

1. A session whose entrypoint is not interactive is **hidden by default**; a setting shows them. Their tokens and spend still count in the power plant, the strip and statistics, so totals stay true.
2. When shown, a scripted run is a **cart or stand** on its district's ground — a small street stall, in the city's own art style — not a building; it opens to the same panel a building does.
3. The setting follows `pkg/config`'s pattern, with `botropolis config` and the settings panel, documented in the man page.
4. Tests: a scripted session makes no building by default; with the setting on, it makes a stall; its spend counts either way.
5. The stall's look is a frame for Aria.

## Answered while building

- **Slice 1's answers** (manager, 2026-10-26): scripted means an `sdk-*` entrypoint; `cli`, empty, IDE extensions and unknown stay buildings. The key is `scripted_runs`, hidden by default or shown. Shown runs are ordinary buildings until slice 2's stall. The hide and show gate is item 274's shared `Shown` filter in `Scene.restate`, with a `Scripted` field. The finder hides them too while hidden, so it matches the map.
- **The stall** (session's plan, approved by the manager, 2026-10-26): four stalls, one per district type, modelled from primitives in `tools/render-sprites/buildings.py` — a hot-dog cart, a bazaar stall, a coffee kiosk and a food trailer — about a third of a footprint and under a storey, keeping the state light, sign and PR flags and no storey extras. A crane over a stall reads wrong, so a stall shows its subagents in flight another way, one small marker per subagent (such as a queue of customers), under Aria's rule that what a mover says at a glance goes somewhere before the mover does. Aria judges the look from the frame.

## Closed

Slice 1 (`a0df84b`, r1115, in 0.3.2) hides a session with an `sdk-*` entrypoint from the map and the finder unless `scripted_runs = "shown"` or the settings panel's *scripted runs* row shows it; with no statistics store, its usage still counts in the breakdown under *off the map*.
Slice 2 (`64ccc26`, r1149) draws a shown one as its district type's stall, with a customer queued at its counter for each subagent in flight, up to five, in place of drones.
`demo/scenarios/stalls.yaml` films them by district type, at night and with a queue forming; Aria judged those frames on 2026-10-26: *"Good, land them."*

Deviations, flagged for Aria:

- **The demo corpus was recorded with `claude -p`**, so staging now writes each placement's entrypoint, `cli` unless it says `scripted: true`; otherwise every film would have lost most of its city.
- **A stall raises no roof scaffold**, since a building's swamped it; its state light already says it is working.
- **The stalls are 1.35 times the size first planned**, which read too small; they still stand lower than a one-storey house.
- **A placement's `subagents: N`** stages made-up subagents at work, because the corpus's finish too fast for a frame to show a queue.
- **Item 280's City Hall and these stalls together exceed z1's `TestKitResidentCost` budget**; the stall size stays unless Aria rules otherwise there.
