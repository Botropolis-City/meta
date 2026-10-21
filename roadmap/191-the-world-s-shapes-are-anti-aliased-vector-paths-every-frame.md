# 191. The world's shapes are drawn as anti-aliased vector paths every frame, and their geometry is most of the city's heap

**Done 2026-10-21 (`afb0540`, r851). Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161 and the benchmark session's measurement.**

Depends on: nothing
Landed: slice 1 (`afb0540`, r851).

## What is wrong

`pkg/render` makes about 100 anti-aliased `vector` calls in the world it draws every frame: `FillPath`, `StrokePath`, and `FillCircle` or `StrokeLine` with anti-aliasing on.
They are scaffold tubes and hoists (`work.go`), spire segments and beacons (`spire.go`), nails and quads (`facade.go`), the plant's stack (`stack.go`), monuments (`monument.go`), group lines (`lines.go`), the City Plan (`cityplan.go`), and power wires, beacons, smoke and glows (`iso.go`).

In Ebitengine v2.10.2 an anti-aliased fill is held back per destination image and drawn later through offscreen stencil images, in several jittered passes (`vector/fill.go`: `FillPath`, `fillPaths`, `offsetAndColorsAA`), so one small circle becomes many vertices and indices.
Non-anti-aliased `FillRect` and `StrokeLine` are one `DrawImage` of a white pixel each, and are cheap.

**Measured** (item 156, `3150e0e`): on the metropolis demo, forcing anti-aliasing off cut the indices a frame 6.6× (734,811 to 112,135) and the live heap from 418 to 142 MB, with the same 476–478 draw commands.
So the cost is the volume of geometry, not extra draw commands or batch breaks.

## The fix

1. **Stamps.** A small set of shapes drawn once at start-up into small managed images, which Ebitengine packs into its shared atlas: a hard disc, a soft disc for glows, a 1-pixel strip for lines and thin quads, a flag.
   World drawing uses `DrawImage` or `DrawTriangles` with `GeoM` and `ColorScale` instead of anti-aliased vector calls: four vertices and six indices a shape.
2. **Quads without stencils.** A filled quad (a facade face, a sign panel) is two triangles through `DrawTriangles` from a white source, with edges that align to the sprite under them; anti-aliasing comes from the stamp's soft edge where it shows.
3. **Out of scope:** UI chrome, unless it draws every frame over the map.
4. **A guard.** `make lint` fails on anti-aliased `vector` calls in per-frame world drawing, with an allowlist for what is composed once into a cached layer, so it does not creep back.

## Judged by

- Item 194's indices a frame, on the same demo, before and after.
- Frames to Aria of the same views before and after: edges must still read as smooth at fit and up close.

## How it was built (2026-10-21)

**One refinement to the fix, agreed with the manager:** lines, quads, rings and filled polygons are not stamps but one small mesh each, drawn from a white pixel, with a one-pixel fringe whose outer vertices are transparent (the technique NanoVG uses).
So every edge stays anti-aliased, not only where a stamp's soft edge shows, still with no stencils and no offscreen passes: a line or a quad is 8 vertices and 30 indices.
Discs are stamps as filed: white discs drawn once, at radii a factor of √2 apart, scaled down by no more than that, so a disc is 4 vertices.
Glows keep their hard edge and `BlendLighter`, so their look does not change; no soft-disc glow was added.
The primitives are `pkg/shapes`; `pkg/render` draws through its `Painter`.

Decisions taken on the way, each answered by the manager:

- **Seams.** A fill's fringe lies wholly outside it, so two fills of one colour that share an edge leave no seam: the GPU gives each pixel on the edge to exactly one core.
  The old anti-aliased fill left a seam 36 levels off on the same two squares; the new one stays within 3 (`testing/integration/shapes`, on Xvfb).
  The cost is that a fill reads about half a pixel larger at its edge, which the kerb strokes over lots and blocks cover; Aria judges it in the frames.
  A stroke's fringe straddles its edge, so a stroke's width stays exact.
- **Joints** are mitred, and bevelled once the mitre would reach past twice its offset, so no wire or group line throws a spike.
  At an acute bevel the inside of the joint is painted twice, which shows only on a translucent colour.
- **Concave fills** are ear-clipped: the L, a notch and the stack's half annulus are tested.
  A ring that crosses itself has no tiling of its own and falls back to a one-pass, non-anti-aliased `FillPath` under the fringe, so it still draws by the non-zero rule.
  The City Plan's coast, a traced ring of thousands of points, is triangulated once and kept for as long as the plan's `CoastShape` says its shape has not changed.
- **Allocation.** Every buffer is the painter's own and reused, so building a frame's shapes allocates nothing (`testing.AllocsPerRun`).
- **Slices 1 and 2 merged:** the conversion reached every per-frame anti-aliased call in `pkg/render`, chrome included, at once.
- **The guard** (`tools/check-antialias`, run by `make lint` and by `testing/acceptance/antialias_test.go`) scans every non-test Go file in the module, reads which functions take an anti-aliasing switch from the vector package's own source, and resolves calls by import path.
  The allowlist is `tools/antialias/allow.txt`, one function a line with its reason; today it holds only the stamp builder.

**Measured**, the metropolis demo at 1600×900, headless, worst settled frame in item 194's `TestTheWorkAFrameTakes`, by day and by night:

| per frame | r844 | item 191 | target |
| --- | --- | --- | --- |
| indices | 766,700 / 777,800 | 75,504 / 78,570 | 20,000 |
| draw commands | 430 / 490 | 277 / 334 | 70 |
| render-target switches | 169 / 175 | 5 / 7 | 30 |

The switches were the anti-aliased fills' offscreen stencil images, so that target is met and now gates.
The Go live heap, from `gctrace` over the same demo, went from about 255 MB to about 125 MB.

The guard and the lowered ceilings landed with slice 1, at r851.
Frames for Aria, before on the left: `botropolis/docs/screenshots/r851-item-191-*.png`.

## Closed (2026-10-21)

Done at `afb0540` (r851): every per-frame anti-aliased vector call in the module is a mesh or a stamp drawn through `pkg/shapes`, and `make lint` keeps them out.
Item 194's `TestTheWorkAFrameTakes` shows the counts above, and its ceilings were lowered to them.
Aria judged the frames (`botropolis/docs/screenshots/r851-item-191-*.png`, landed at r852): *"All those changes look solid."*

Deviations from the item as filed, each agreed with the manager:
lines, quads and rings are fringed meshes rather than stamps, so every edge stays smooth;
there is no soft-disc glow, so glows look as they did;
filled shapes read about half a pixel larger, the price of no seams;
and slices 1 and 2 landed as one.
The bug Aria spotted in the night crop, lit windows drawn over a district sign, was there before this item and is filed on its own.
