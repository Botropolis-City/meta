# 323. The hero loop's sea ends inside the frame: a black wedge in the top-right corner

**Fixed 2026-11-02 (`d19d933`, r1221). Filed 2026-10-28 (r1209), from 0.3.4's re-film, flagged by the filming session. Nobody's call — a defect; Aria judges the frame.**

`dist/demo/metropolis/loop.mp4`, the website's hero video, shows a black wedge in its top-right corner for the whole clip, and a second one bottom-right partway through: the drawn sea ends inside the camera's frame at the hero's zoom and angle.
0.3.3's loop, filmed from `77ae413`, has the same wedge at the same place, so it is live on botropolis.city today and not new in 0.3.4; the 4:5 cut and the hero and card stills do not show it.

## The fix

The sea (or the sky beyond it) covers the whole frame at every zoom and angle the demo's camera reaches: either the sea's extent follows the camera, or the clear colour outside the sea is the sea's own.
A test on the hero scenario: no pixel of its frames is the clear black.

## Closed

The ground under the sea texture was cleared to the void; it is now cleared to the light's own sea colour whenever there is an island, so no pan or zoom finds the sea's edge (`d19d933`, r1221; build tag `3337704`, r1222).
`TestTheHeroLoopsSeaFillsTheFrame` records the loop as the film does and finds no clear-coloured pixel in any frame it keeps; before the fix every one had 10–21 thousand.
It skips the one-second lead the film discards, where the interface is still up and 9 of its pixels match the clear colour.
Aria passed the loop's 6 s frame on 2026-11-02; the hero is re-filmed with 0.3.5 (item 327).
