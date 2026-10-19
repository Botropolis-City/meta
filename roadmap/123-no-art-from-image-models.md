# 123. Write down the art rule: no art from image models

**Done 2026-10-18 (`e1c6472`, r661). Filed 2026-10-18 (r628), Aria's decision after the art audit of items 119–122. Nobody's call — Aria has decided; this records and guards it.**

Aria, 2026-10-18: *"document my art decision to not use ai generated art but to instead use real artists or open source assets or generate art only by generating polygons and such through blender just as an artist would and so we don't rely on any models trained on art they may inadvertantly use other's art."*

## The decision

Every picture Botropolis draws, ships or publishes comes from one of three places:

1. **A human artist**, credited, and paid when the work is commissioned.
2. **An openly licensed asset pack**, with its licence followed, its licence file committed beside what was taken from it, and its author thanked — today, Kenney's CC0 kits and Inter under the OFL.
3. **Geometry built by hand in code**: primitives placed, sized and coloured in a Blender script (`botropolis/tools/render-sprites/`) or shapes drawn in Go (`botropolis/pkg/render/`), the way an artist models.
   Claude writing that code is allowed, because what it writes is geometry, not a picture.

What is ruled out is **any model whose output is a picture, a texture or a mesh**: image generators, AI texture tools, image-to-3D and text-to-3D, and AI upscalers.
Those models are trained on artists' work and can reproduce it without anyone knowing, and the reason for the rule is to keep that out of the city.

The same rule covers the website, the logo, the icons and the demo frames.
Frames rendered from the app are the app's own art and so fall under it already.

## Where it stands today

The audit of 2026-10-18 found the rule already holds:

- All 155 atlas sprites are either from Kenney's kits, each with its `License.txt` in `botropolis/pkg/assets/kits/`, or modelled from boxes and cylinders in `buildings.py` and `render.py`.
  The in-house ones are the 95 under `botropolis/`.
- The 16 px packs are Kenney's, with licences.
- The logo, `botropolis/packaging/botropolis.svg`, is twelve hand-placed polygons.
- Monument signs, scaffolding, badges, the river and wires are vector shapes drawn in Go.
- The three images in `docs/references/` are diagrams and crops of the project's own renders.
  The photographs Aria gave for the monument sign (bug 45) were references to build from, as an artist uses them, and were never committed.

Items 119–122 fix where the credit is missing.
None of them is a breach of this rule.

## The work

1. **Record it** in a design document, `botropolis/design/art-sources.md`, listed in `botropolis/DESIGN.md`'s *What exists* table, holding the three sources, what is ruled out, and why.
   Add one line each to `botropolis/CLAUDE.md` and `botropolis.city/CLAUDE.md` pointing at it, so every session that touches art reads it before it starts.
   Add a line to `roadmap/art-direction.md` noting that its *Held in reserve* pack, Quaternius's CC0 robots, is source 2 and passes.
2. **Guard it.** A check, run by `make lint`, that every image under `botropolis/pkg/assets/` either sits in a directory with a licence file or is a page that `tools/render-sprites` produces and `make sprites-check` reproduces.
   An image that is neither fails, naming the file.
   Mutate it red before trusting it: add an unlicensed PNG under `pkg/assets/` and watch it fail.
   This catches an asset with no traceable source.
   It cannot tell whether a picture came from an image model, so the written rule stays the guard for that.

## Done when

The design document is written and listed, both `CLAUDE.md` files point at it, and the asset-source check fails on an unlicensed image and passes on the tree.

## Closed

Done 2026-10-18 in botropolis `e1c6472`, r661, in one slice.

- `botropolis/design/art-sources.md` holds the three sources, what is ruled out and why, what the rule covers, and what guards it; `DESIGN.md`'s *What exists* table lists it.
- `botropolis/CLAUDE.md` has an *Art* section pointing at it,
  and the manager added the line to `botropolis.city/CLAUDE.md` (botropolis.city `60d541b`).
- [art-direction.md](art-direction.md) notes that the Quaternius robots held in reserve are source 2 and pass.
- `tools/check-asset-sources`, run by `make lint` and by `testing/acceptance/asset_sources_test.go`, walks `pkg/assets/` on the filesystem and fails, by name, on any image (by extension or leading bytes) with neither a non-empty licence file beside it nor a `kits-z*.json` manifest in `pkg/assets/kits/` naming it as a page; it also fails on a missing or image-less `pkg/assets/`.
  On the tree it reports 3 licensed images and 8 rendered pages.
- Mutated red: an unlicensed PNG added to the real `pkg/assets/` failed by name, and the test's seven fixture mutations (unlicensed PNG, JPEG and SVG, a PNG renamed `.bin`, an unmanifested page beside the atlases, a manifest outside `kits/`, an empty licence file) each fail.
  Five faults put into the guard itself — accepting an empty licence, dropping the leading-bytes check, accepting any `kits-z` name anywhere, passing an empty corpus, passing a missing `pkg/assets/` — were each caught by their own test.
  A row in `TestScriptsAreInTheCacheKey` makes an edit to the script re-run the test.

No deviation from the item.
The guard cannot tell whether a picture came from an image model, and the design document says so: the written rule is the guard for that.
No changelog entry, because nothing a user of Botropolis sees changed.
