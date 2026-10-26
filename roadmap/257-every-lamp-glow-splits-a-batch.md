# 257. Every lamp's glow splits the frame's batch, so new lamps cannot be afforded at night

**Open. Filed 2026-10-26 (r1058), from item 247. Nobody's call — the night draw ceiling is set (37).**

Depends on: 247

[Item 247](247-no-road-leads-to-a-bridge.md) laid a road to each bridge, with street lamps like every road's; on the metropolis at night they took the frame from 37 draw commands to 40 against `TestTheWorkAFrameTakes`'s ceiling of 37 (measured, four runs each: no lamps 36, district roads' lamps 37, with the bridge road's 40).
Aria chose, 2026-10-26, to land item 247 with its bridge road unlit and get the lamps back through this item.

**The mechanism**, from item 247's session: the still city is composed once ([item 193](193-a-still-city-is-redrawn-whole-every-frame.md)) and only rectangles where something moves are replayed; `batch()` reorders replayed draws by source only past draws they do not overlap, so the frame stays identical.
A lamp's glow is an additive disc (`BlendLighter`) laid right after its own sprite and overlapping what is drawn over it, and additive light and a sprite over it do not commute, so the glow's place is pinned and splits the run on each side: about one or two commands per lamp inside a moving rectangle.

## The fix

Lay every lamp's glow in a light layer of its own, cut by whatever stands in front through the punches and cuts the windows already use ([item 195](195-lit-windows-are-drawn-over-district-signs.md), [item 236](236-where-a-vehicle-stands-changes-a-frames-draw-count.md)), and composite it additively once.
Every glow then batches; since today's 37 already pays for the district roads' lamps, the city likely comes in under it.
Laying a glow and then cutting it by a sprite gives the inline order's pixels except where additive light clips at white, so the frame check compares against the inline order with that stated tolerance, and the difference is shown to Aria.
Then put the lamps back on the bridge road and its joints.

Tests: `TestTheWorkAFrameTakes` at night at or under 37 with the bridge road lit (the ceiling ratchets down if it falls); the frame check against the inline glows; frames by night, at fit and zoomed in, of the bridge road lit, for Aria. Item 212's record reuse journals light ops, so its walk must hold too.
