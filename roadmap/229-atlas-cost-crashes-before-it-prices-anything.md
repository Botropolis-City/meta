# 229. `tools/atlas-cost.py` crashes before it prices anything

**Fixed 2026-10-24 (`094b6f7`, r972). Filed 2026-10-24 (r969), found by item 162's session during its slice 14. Nobody's call — a defect in a tool.**

On `main`, `python3 tools/atlas-cost.py` in `botropolis/` stops at once:

```text
    exec(re.search(r"^PIECES = \{.*?^\}", src, re.M | re.S).group(0), ns)
  File "<string>", line 55, in <module>
NameError: name 'buildings' is not defined
```

**The mechanism.** `pipeline()` in `tools/atlas-cost.py` reads `tools/render-sprites/render.py` as text, cuts out the `PIECES = {…}` literal with a regex, and `exec`s it alone in an empty namespace.
Since item 109's slice 4 (`9c84fbd`, 2026-10-18), the `botropolis` kit's list in `PIECES` is not a literal: it adds `buildings.names()`, `buildings.course_names()`, `buildings.site_names()` and `buildings.ruins_names()` from `tools/render-sprites/buildings.py`, which the cut-out never imports.
So the tool has not run for six days, and nothing noticed, because nothing calls it ([bug 24](024-a-third-of-the-atlas-never-drawn.md) wrote it as a one-off measure).

**The fix.** Read `PIECES` by importing `render.py`'s module, or `buildings.py` into `ns` before the `exec`, so the tool sees the list the renderer packs; importing is the sturdier choice, since the next non-literal would break the regex again.
Its test: a run of `tools/atlas-cost.py` on the repository's own `render.py` exits 0 and prices every page, so the tool cannot rot silently again; put it where the other tool checks run, so `make lint` or `make test` calls it.

## Answered while building

- **The test tree** (manager, 2026-10-24): approved as sent, `TestAtlasCost` in `testing/acceptance/atlas_cost_test.go` with `atlas-cost.py` importing `render.py` as a module under stand-in `bpy` modules; one change: the zoom levels are read from the shipped `kits-z*.json` files, not listed, since item 162's slice 14 adds a z1.5 level.

## Closed

Fixed in `094b6f7` (r972).
`tools/atlas-cost.py` now imports `render.py` as a module, with stand-ins for the Blender-only modules, which neither `render.py` nor `buildings.py` uses at module level,
so `PIECES`, `PAGE` and `PAD` are what the renderer packs however they are built.
Its caller is `testing/acceptance/atlas_cost_test.go`, run by `make test`: every zoom with a shipped `kits-z*.json` replays its page count exactly, nothing says MISMATCH, the whole atlas is priced, and `--drop-unused` exits 0.
The test opens the files the tool reads, so the Go test cache cannot replay a pass against a different tree.

**A deviation, flagged for Aria: the fix went past the crash.**
Once it ran, the tool printed `z2: 6 pages (MISMATCH — shipped 5)`, because its copy of the shelf packer predated item 162's slice 11, which moved the renderer to `pack.py`.
That was a second rot behind the first,
and fixing only the import would have left a tool that runs and lies.
It now calls `render.py`'s own `pack.pack` over the sprites in the renderer's (piece, heading) order rather than a copy, and reads each zoom's shipped page count from its manifest.
Both zooms now replay exactly.
