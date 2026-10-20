# 166. Lit windows at night are round halos, not the building's windows

**Open, in progress since 2026-10-19 in the session "item 166". Filed 2026-10-19 (r782) at Aria's request, from item 155's frames. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`77f8b82`, r783).

[Item 155](155-windows-light-as-each-floor-is-finished.md) lights a building's windows floor by floor at night, at the right storeys; Aria passed the timing.
But the glow is still drawn as soft round halos per window position (`nightLights`, `botropolis/pkg/render/iso.go`), so a lit building reads as a grid of discs rather than lit windows (`botropolis/docs/screenshots/r781-item-155-build-at-night.png`).
Aria, 2026-10-19: *"The timing is right but we still have round circles. We need the glow to match exactly where the asset's windows are, just like we do with boarded up windows. That actually makes me wonder what that looks like on the new buildings. Can I see a mockup of all the new buildings at every tier both normal and boarded up times both night and day?"*

## Slice 1 — the mockup, before anything changes

One contact sheet of every building kind the city draws (residential, shopping, office, industrial, each at every height tier 1–5, plus anything else a session's building can be, such as ruins), each drawn four ways: **normal by day, normal by night, boarded up by day, boarded up by night**, at map scale and the default heading, labelled. It shows today's rendering, so Aria sees where boarded-up windows and night glow already fit each piece's windows and where they don't. Commit it to `botropolis/docs/screenshots/` and send it for her to judge before slice 2.

**Made** (`77f8b82`, r783): `botropolis-demo sheet --out FILE [--zoom Z]` draws it with the map's own calls on a private virtual display, so slice 2's "after" is the same command.
The sheets, at r783 (`1d0d2e7`): at map scale, `botropolis/docs/screenshots/r783-item-166-buildings-before.png`, and at zoom 2, `botropolis/docs/screenshots/r783-item-166-buildings-before-zoom2.png`.
They are cited as paths because the main botropolis checkout had not pulled them when this was written.
Ruins are only ever a resting session's, so they are never lit; their "normal" row is resting behind blinds.
What they show: the night glow is three discs a storey on every lit piece, sitting across the windows rather than on them; boarded-up planks fit the panes on residential, shopping and office; on industrial, whose windows are ribbons, the planks on the right face run past the building's edge.

## Slice 2 — glow from the windows themselves

Night glow lights each piece's actual window panes, the same window geometry the boarded-up overlay already uses (`botropolis/pkg/render/facade.go` and its callers), tinted warm, with at most a faint bloom that follows the pane shape — no round halos. Item 155's rules hold: only finished storeys light, nothing above the built height. Any piece whose windows aren't known yet gets them measured (as the boarded-up work did), not estimated.

Tests: every building kind × tier has window geometry; the lit pixels at night fall inside its window panes (none outside a small bloom margin); boarded-up and lit use the same panes; item 155's storey tests still hold. Then the same contact sheet again for Aria, after.
