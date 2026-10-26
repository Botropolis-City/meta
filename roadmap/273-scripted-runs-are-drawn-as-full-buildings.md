# 273. Scripted, non-interactive runs are drawn as full buildings

**Open, in progress since 2026-10-26 in the session "item 273". Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — Aria ruled; the stall's look is a frame for her.**

Depends on: nothing
Landed: slice 1 (`a0df84b`, r1115).

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
