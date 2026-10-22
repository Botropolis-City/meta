# 199. Night-light cuts land on shared textures in a different order each run, so the frame's draw count varies

**Fixed 2026-10-22 (`0d91687`, r909). Filed 2026-10-21 (r880), found by item 162. Nobody's call — a defect in a gate's determinism.**

Depends on: nothing

[Item 194](194-nothing-counts-the-work-a-frame-takes.md)'s `TestTheWorkAFrameTakes` counts a settled night frame's draw commands. On `github/main` (`cedcaaf`) six runs of the same debug city settled at **40, 40, 40, 41, 42, 40**, each constant within its run.
Item 162 diffed a 40 against a 42: [item 195](195-lit-windows-are-drawn-over-district-signs.md)'s night-light cuts (destination-out stamps) alternate between two of Ebitengine's shared 1024² atlas textures, in an order set by where each stamp happened to be packed, and every alternation is a separate command.
So the count depends on packing, not on the city, and the regression ceiling (taken from one run) sat below main's own range; item 162 raised it to 42 with that reason.

## The fix

Give the light stamps and cut shapes a texture of their own (unmanaged, as [item 193](193-a-still-city-is-redrawn-whole-every-frame.md) did for looks and labels), so every cut draws from one source and batches. Then the count is the same every run.

Tests: ten runs of the night frame give one count; the night ceiling comes back down to it (+2%), and the comment saying why it was 42 goes.

## Fixed (2026-10-22, `0d91687`, r909)

Six runs on `github/main` at `e6bde10` settled at 42, 42, 42, 41, 41, 41.
Diffing a 40 against a 41 in Ebitengine's command log found three causes, not one, each a texture change in the run of destination-out cuts:

1. **The painter's stamps were packed into shared atlases.** It told the cutter of the images it draws with, its white pixel and about nineteen disc stamps, and Ebitengine packs each into whichever shared atlas has room. The fix the item names: one unmanaged sheet holding all of them, which the cutter is told of instead (`pkg/shapes/cutsheet.go`). The painter still draws from its own images, so the day frame does not move.
   That alone was not enough: four runs gave 41, 43, 42, 40.
2. **The standing city's leftover cuts were sorted by pointer.** `layLightsStream` tiebroke on the address of each sprite's image, which differs every run, so the punches from two pages interleaved differently each time. Sorting without the tiebreak was deterministic but cost 47, because nothing grouped the pages.
   So each punch now carries the page its sprite is cut from, and both cut layers share `orderCuts`: a kind at a time, then a page at a time in the order the pages were first noted.
3. **A shrunk punch is drawn from a mipmap.** One 2048² kit page still showed as two textures, 1024² and 512², alternating: Ebitengine draws a downscaled sprite from the mipmap level its scale picks. A page's punches are now laid largest first, so each level is one draw. Disabling mipmaps would have done it too, but it would change how a shrunk sprite's cut edge looks.

With all three: four runs settle at **39, 39, 39, 39**, below main's best.
The night ceiling is 39 (+2% rounds to nothing below one command), and the comment explaining 42 is gone.
The day frame drops from 23 to 22, and its ceiling stays at 23.

Tests (tree approved by the roadmap manager, four runs in place of ten to keep the acceptance suite's cost down):
the night case of `TestTheWorkAFrameTakes` runs four times at once and asserts one count;
`TestPainterCuts` asserts that the cutter is told only of stamps on the cut sheet, that no two overlap, and that the sheet is unmanaged;
`TestTheOrderCutsAreLaidIn` asserts the kind order, the page grouping, and the size order within a page.

Deviations for Aria: the item named one cause and there were three, so the fix also orders punches by page and size, which changes `punch`, `drawSprite` and `kitPlace` in `pkg/render`.
The acceptance test runs four times rather than ten, as the roadmap manager decided.
No frame to judge: reordering destination-out cuts does not change pixels, and the sheet's stamps are drawn exactly as the painter's own.
