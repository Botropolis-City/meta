# 217. A delivery truck can leave the island beside the bridge instead of on it

**Open. Filed 2026-10-24 (r966) at Aria's request, from the 0.3.0 website clip "A day on two projects". Nobody's call — a defect.**

Aria, 2026-10-24: *"in the video of a day on two projects, the green car leaves the screen not on the bridge"*.

**What the clip shows** (`botropolis/dist/demo/timelapse/day.mp4`, filmed 2026-10-23 from v0.3.0; the same clip is on botropolis.city):
- **The first merge (scenario `timelapse`, at 24 s): wrong.** The green delivery truck leaves the island running parallel to the bridge along its north side, over the shore and then the water, never on the deck. Reproduce with `ffmpeg -ss 28 -i day.mp4 -t 4 -vf "fps=2,crop=520:300:250:350,tile=4x2"`: the truck is at roughly (455,105) → (420,75) → (325,25) in successive frames of that crop, above the deck rather than on it, until the camera pans away at 32 s.
- **The second merge (at 46 s): right.** That truck drives onto the ramp and along the deck (`-ss 47 -t 7`, crop `900:520:200:280`).
So the route is not wrong every time, which rules out the bridge's geometry alone.

**Where it is.** `City.toBridge` (`botropolis/pkg/city/pullrequests.go`) builds the truck's path: the building's kerb, its driveway, the avenues from `walkStreets` to `bridgeCell`, then `bridge.Land` and `bridge.Far`. `render.deliveryAt` (`pkg/render/bridge.go`) raises it onto the deck only while `Bridge.Rise(at) > 0`. Candidates to check first:
- the keep-to-the-right lane offset from [item 153](153-cars-keep-to-the-right.md), applied on the bridge stretch where the deck is narrower than an avenue, or from a different heading when the last avenue cell meets `bridge.Land` at an angle (the two trucks start in different districts, kiln and tidepool, so they reach `bridgeCell` differently);
- a truck drawn at ground level while the deck is raised ([item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md)'s ramp), which on screen sits beside the deck rather than on it;
- the path's last avenue cell not being the bridge's landing cell, so the final leg cuts across.

## The fix

Find which of these it is from the first truck's actual path and drawn position, then keep every truck on the deck from the landing to the far end, at every heading.

Tests: for a truck leaving from each district of a city, every point of its path from `bridge.Land` on lies within the deck's width, and its drawn position is raised by the deck's rise wherever `Rise > 0`; a frame of both of the timelapse's trucks on the bridge for Aria.
