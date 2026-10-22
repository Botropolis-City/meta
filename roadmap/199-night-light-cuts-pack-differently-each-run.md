# 199. Night-light cuts land on shared textures in a different order each run, so the frame's draw count varies

**Open. Filed 2026-10-21 (r880), found by item 162. Nobody's call — a defect in a gate's determinism.**

Depends on: nothing

[Item 194](194-nothing-counts-the-work-a-frame-takes.md)'s `TestTheWorkAFrameTakes` counts a settled night frame's draw commands. On `github/main` (`cedcaaf`) six runs of the same debug city settled at **40, 40, 40, 41, 42, 40**, each constant within its run.
Item 162 diffed a 40 against a 42: [item 195](195-lit-windows-are-drawn-over-district-signs.md)'s night-light cuts (destination-out stamps) alternate between two of Ebitengine's shared 1024² atlas textures, in an order set by where each stamp happened to be packed, and every alternation is a separate command.
So the count depends on packing, not on the city, and the regression ceiling (taken from one run) sat below main's own range; item 162 raised it to 42 with that reason.

## The fix

Give the light stamps and cut shapes a texture of their own (unmanaged, as [item 193](193-a-still-city-is-redrawn-whole-every-frame.md) did for looks and labels), so every cut draws from one source and batches. Then the count is the same every run.

Tests: ten runs of the night frame give one count; the night ceiling comes back down to it (+2%), and the comment saying why it was 42 goes.
