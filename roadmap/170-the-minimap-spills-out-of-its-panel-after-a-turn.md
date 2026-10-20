# 170. After the camera turns, the minimap comes up at fit and its map spills out of its panel onto the footer

**Open, in progress since 2026-10-20 in the session "item 170". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

After one press of `r`, at fit, a minimap appears in the bottom-right corner that is not there before the turn, and what it draws does not sit in its panel.
Its rounded panel is at about (1744, 937)–(1904, 1032), but its map — the ground fill and the viewport box — is drawn from about (1811, 982) to (1905, 1056): off the panel's right edge, and down through the footer, which starts at y = 1027.

![The minimap after one turn](../docs/references/170-minimap-after-a-turn.png)

Shot: `buildings`, `r` once, at fit, 13:00, 1920×1080, filmed by `make demo-media` with a scenario of stills only; the crop is (1500, 880)–(1920, 1080) at twice size.
It is the same after two and three turns, at fit and at closest zoom, in every scenario the audit filmed; without a turn the minimap is either absent at fit or drawn inside its panel at zoom.

## The mechanism, as far as it was cheap to find

`(*Game).minimap` (`botropolis/pkg/render/ground.go`) gets its frame from `Scene.Minimap` (`botropolis/pkg/city/scene.go`), which scales `camera.Bounds(city.Extent())` into the box, and then draws `m.ProjectRect(c.Bounds())` and the districts through it without clipping to the box; only the viewport rectangle is clamped.
Two things look wrong after a turn, and either may be the whole of it:

- it is shown at all: it hides only when the projected view contains the projected city, and after a turn at fit it does not, so either the turn leaves the camera not quite at fit, or the containment test compares boxes from two different projections;
- its contents land outside the box, which the box's own scale and origin should make impossible, unless `bounds` and the rectangles projected through it are taken under different headings.

The fix wants a test in `pkg/city` that turns a fitted scene and asserts that every rectangle `Minimap` projects lies inside its box, and that a fitted scene, turned, still reports that its view holds the whole city.
