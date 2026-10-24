# 243. A kind tag over a building across the screen's edge is left out of the composed frame

**Fixed 2026-10-24 (`f3c27d0`, r1016). Filed 2026-10-24 (r1014), found by item 240's session when its slice 2 failed to land. Nobody's call — a defect; item 240's session fixes it.**

Depends on: nothing

[Item 193](193-a-still-city-is-redrawn-whole-every-frame.md)'s check, `TestTheStillCityMatchesTheCityDrawnDirectly` (`botropolis-demo sheet --check-frames`), fails on [item 240](240-the-metropolis-demo-reads-as-a-light-user.md)'s heavier metropolis "at full zoom, a building across the edge", in every frame by day and by night: 2,343 pixels in (1240,841)–(1358,861) differ from the city drawn straight.
The composed frame, the standing city reused, leaves out the kind tag *"flag · a pull request"* that the straight frame draws over a flagged building.
The heavier history changes the buildings' heights, which puts a flagged building across the screen's edge at full zoom; the same metropolis staged without `pace:` passes.
So it is a gap in the composed path that the scene exposes, as with items 223 and 236, and no pace that happens to dodge the shot fixes it.

## The fix

Draw a kind tag over a building across the screen's edge in the composed frame exactly as the straight frame draws it.
Test first in `pkg/render`: a kind tag over a building cut by the frame's edge is in the composed frame as in the straight one; then `--check-frames` passes on the paced metropolis.

## Answered while building

- **The cause, which turns the item round** (the session "item 240", 2026-10-24, agreed by the manager): the tag is not a kind tag the composed frame loses but a first-sighting caption, *"flag · a pull request"*. Captions are chosen from the things drawn so far in the frame (`pkg/render/explain.go`), and the straight drawing, the check's reference, draws every building, off-frame ones too (item 161), so it picked a flag off the window and `ui.LayoutExplain` clamped its caption to the window's edge, pointing at nothing visible; the composed drawing, which is what the city shows, culls off-frame buildings and rightly captions nothing. Whether a sighting is still up when the edge variant is drawn depends on the frame count, which is why the light metropolis passed. The title stays, since the filename is cited.
- **The fix and its tree** (manager, 2026-10-24): a caption, first sighting or explain mode, considers only things whose hit box overlaps the window, so the two drawings agree and no caption points off-screen; the city shows no change, since it already culls. `TestCaptionsNameOnlyWhatIsOnTheWindow` in `pkg/render`: nothing captioned when the only one of its kind lies off the window; the one on the window captioned when one lies off and one on; explain mode not captioning a kind drawn only off the window. Then `--check-frames` passes on the paced metropolis at 30 frames.

## Closed

Fixed as answered above in botropolis `f3c27d0` (r1016): `explainCaptions` keeps only what overlaps the window, before it sights a kind, so an off-screen thing neither gets a caption nor spends its first sighting.
`TestCaptionsNameOnlyWhatIsOnTheWindow` (in its own file, `pkg/render/captionwindow_test.go`) was red on the two off-window cases before the fix; it also holds, as the manager asked, that a thing crossing the window's edge is still captioned.
`botropolis-demo sheet --check-frames` on the paced metropolis at 30 frames now passes by day and by night, where it failed at full zoom, a building across the edge.

**Deviation, flagged for Aria:** the item asked for the composed frame to draw the tag as the straight one did; the straight frame was the one in error, so the fix is to the captions both drawings lay out, and the city shows no change.
No changelog entry, since nothing a user sees changed.
