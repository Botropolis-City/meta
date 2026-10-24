# 243. A kind tag over a building across the screen's edge is left out of the composed frame

**Open, in progress since 2026-10-24 in the session "item 240". Filed 2026-10-24 (r1014), found by item 240's session when its slice 2 failed to land. Nobody's call — a defect; item 240's session fixes it.**

Depends on: nothing

[Item 193](193-a-still-city-is-redrawn-whole-every-frame.md)'s check, `TestTheStillCityMatchesTheCityDrawnDirectly` (`botropolis-demo sheet --check-frames`), fails on [item 240](240-the-metropolis-demo-reads-as-a-light-user.md)'s heavier metropolis "at full zoom, a building across the edge", in every frame by day and by night: 2,343 pixels in (1240,841)–(1358,861) differ from the city drawn straight.
The composed frame, the standing city reused, leaves out the kind tag *"flag · a pull request"* that the straight frame draws over a flagged building.
The heavier history changes the buildings' heights, which puts a flagged building across the screen's edge at full zoom; the same metropolis staged without `pace:` passes.
So it is a gap in the composed path that the scene exposes, as with items 223 and 236, and no pace that happens to dodge the shot fixes it.

## The fix

Draw a kind tag over a building across the screen's edge in the composed frame exactly as the straight frame draws it.
Test first in `pkg/render`: a kind tag over a building cut by the frame's edge is in the composed frame as in the straight one; then `--check-frames` passes on the paced metropolis.
