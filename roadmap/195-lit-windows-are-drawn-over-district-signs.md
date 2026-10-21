# 195. Lit windows are drawn over district signs at night

**Open, in progress since 2026-10-21 in the session "item 195". Filed 2026-10-21 (r852) by Aria, from item 191's night frames. Nobody's call — a defect.**

Depends on: nothing

In `botropolis/docs/screenshots/r851-item-191-night-3x.png` (both halves, so it predates item 191), the tower behind the "orchard / your move" district sign shows its lit windows straight through the sign: yellow panes run across the sign's board and its words.
Aria, 2026-10-21: *"the window lights are drawn over the label. The label should be in front."*

The lit windows come from [item 166](166-lit-windows-are-round-halos-not-windows.md)'s lights layer, which is laid over the scene after it is drawn, and a sprite drawn later in the depth sort cuts its shape out of that layer. The sign is drawn in front of the tower but does not cut the layer — so it is either drawn outside the depth sort the cuts are taken from, or as a label after it. Find which, and check every other thing drawn over buildings the same way: station plates, badges, map labels, the hover card, the move tones, the group stations kept on top by item 179.

## The fix

Everything that should sit in front of a lit building either cuts its shape from the lights layer or is drawn after the layer is composited. Labels and signs should be after it, since they are not part of the scene's depth.

Tests: `--check-lights` gains a lit tower with a district sign in front: no lit pixel inside the sign's board. The same for a station label and a badge over a lit building. A night frame for Aria at the same crop.
