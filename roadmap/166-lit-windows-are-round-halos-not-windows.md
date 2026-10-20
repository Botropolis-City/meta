# 166. Lit windows at night are round halos, not the building's windows

**Fixed 2026-10-20 (`a6025e8`, r785). Filed 2026-10-19 (r782) at Aria's request, from item 155's frames.**

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

## Fixed

**Aria's verdict on the sheet** (2026-10-19): the discs looked completely wrong, and every building already looks lit by day. She chose between two options mocked on the same sheet: A, night darkens the building but not its windows, which keep their day brightness; or B, day mutes the windows and night shows them as A. **She picked A**, and approved its mockup as the target.

**At night a lived-in building's own windows are lit** (`a6025e8`, r785): each lit pane is the sprite's own pixels, drawn again from the atlas page over the night wash, at day brightness, all of a building's panes in one call (`botropolis/pkg/render/windows.go`). There is no tint and no bloom: option A replaced both. While a building rises only its finished storeys' panes light (item 155), each pane's storey measured from the ground of its own face, because a storey is a sloped band across a face. Boarded-up buildings and ruins never light.

**Every window is now measured, not estimated** (`tools/render-sprites/render.py`): glass patches touching at corners, split at the building's near corner, enclosed at the projection's slope (which way, told by the edge that runs nearest it) and pushed out until every pixel of glass is inside. A patch is a window only if it holds core glass, by a colour rule the atlas manifest now carries so the map's tests tell glass the same way; that keeps the shopping awning's trim and the billboard out, and lets the industrial transoms in. `make sprites` reproduces the manifests byte for byte.

**Planks fit too**: on a pane wider than it is tall they stop at the glass, so industrial planks no longer hang off the corners, and every plank is held to the building's own pixels row by row.

**Two faults found after slice 2 landed, both fixed:**
- A side review found the lights were drawn after the whole scene, so a building's windows painted over anything in front of it. Each building's windows are now noted in depth order and every sprite in front of them cuts them out, laid in a lights layer after the scene (`7b685e4`, r788; `e566a0e`, r789).
- A first version cut a layer of each sprite's glass at start-up, which put about 20 MB on the start-up heap's peak and failed `TestStartUpPeak`'s 240 MB; drawing from the atlas page keeps nothing and is back to baseline.

**Tests**, each mutated red: every glass pixel lies inside a pane, every pane stays on the building's own pixels and on one face at the projection's slope, every plank stays on the building, a half-built building lights only its finished storeys, one window draw per standing building; and `botropolis-demo sheet --check-lights` (acceptance) draws every kind lived in and boarded, standing and half built, and a lit tower behind a dark building, and fails on any lit pixel off the panes that should be lit. `BenchmarkDrawANightFrame` reports the night's cost: on the metropolis demo, 351 sprites a frame by day and by night, and at night 17 window draws and 97 cuts, where the discs were three path fills per lit storey.

**Frames**, all approved by Aria on 2026-10-20: the sheet after, `botropolis/docs/screenshots/r785-item-166-buildings-after.png` and `r785-item-166-buildings-after-zoom2.png`, the same command as the before sheet; and a dense district at night, `botropolis/docs/screenshots/r788-item-166-district-at-night.png` (drawn at `e566a0e`, which became r789 when item 174 landed ahead of it). Cited as paths because the main botropolis checkout had not pulled them when this closed.

**Left for later**: lighting the landmarks at night (the library, City Hall, the power plant) is a follow-up item, filed by the manager at Aria's request.
