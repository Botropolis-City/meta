# 191. The world's shapes are drawn as anti-aliased vector paths every frame, and their geometry is most of the city's heap

**Open, in progress since 2026-10-21 in the session "item 191". Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161 and the benchmark session's measurement. Nobody's call — the fix is known.**

Depends on: nothing

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
