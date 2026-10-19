# 99. Landmark labels sit on the neighbouring district

**Fixed 2026-10-19 (`631b41a`, r701). Filed 2026-10-16 (r510) at Aria's request, from frames of items 86 and 88. Nobody's call — a defect.**

Landed: slice 1 (`5e70cb3`, r676).
Landed: slice 2 (`5fd2ef2`, r684).
Landed: slice 3 (`e5f0e5a`, r692).
Landed: slice 4 (`631b41a`, r701).

The "power plant" label is drawn beside the kiln district's plaque rather than on the power plant, in `docs/screenshots/r470-item-86-ladder.png`, `r490-item-86-ladder.png`, `r505-item-86-overgrown.png` and `r488-item-88-district-signs.png`, and the library's label is just as far from the library.

Both labels anchor at the projected `Rect.Min` of the landmark's plot (`botropolis/pkg/render/game.go`, the `if labels` blocks for `c.Plant` and `c.Library`).
In the isometric projection that corner is the plot's back corner, which lands on or beside whatever stands behind it, here a district's plaque.

The fix: anchor each landmark's label on the landmark itself, over the top of its drawn sprite, the way district and building signs are placed, and test that the label's point lies within the landmark's projected bounds at every heading.

## Closed

**The diagnosis above named the wrong code.**
The `game.go` blocks draw only the top-down view, which item 106 retired; every frame cited is isometric, and its labels came from `isoLandmarkLabels` in `botropolis/pkg/render/iso.go`.
That placed each label a sprite's full height above the landmark's foot, but a sprite's top is only its anchor's height above the foot, so the label floated too high by everything below the anchor, about 100 px at r505, onto kiln's plaque behind the plant.
City hall's label had the same fault.

It closed in four slices, the last three at Aria's direction from the frames:

- Slice 1 (`5e70cb3`, r676) placed the labels from the rect the sprite is drawn into, in item 102's label layout.
  Aria saw them still sit by kiln's plaque.
- Slice 2 (`5fd2ef2`, r684) rested them on the roofs; Aria turned that down, since it covers the roofs' animation, and asked for something that is not a HUD label.
  Mock-ups of a façade lettering and a lot-edge plaque went to her, and she picked the façade.
- Slice 3 (`e5f0e5a`, r692) turned the plant, the library and city hall 180° so their fronts face the home heading, as she asked, the plant's chimney with it, and painted each name on a clear band of a wall the camera sees, never across a door or window.
  The landmark's plate shows only on hover.
- Slice 4 (`631b41a`, r701) moves a name that a nearer landmark would hide to the band's uncovered half, stacked if it is two words, never below `ui.MinSignPx`.

The walls, doors, windows and bands are measured by hand in `botropolis/pkg/render/landmarkwalls.json`, because the atlas records panes for two of the three and doors for none.
That table pins a hash of the sprite pixels it was measured from, so re-rendered art fails `TestLandmarkWallsAreMeasuredFromTheArtInTheAtlas` instead of leaving it quietly stale, and `botropolis/tools/landmark-walls` draws the table back over the sprites to re-measure.
The tests are in `botropolis/pkg/render/landmarksign_test.go`, each mutated red before it was trusted.

The frames are `botropolis/docs/screenshots/r692-item-99-lettered-h0.png`, `-h90`, `-h180` and `-h270`, and `r701-item-99-unhidden-h0.png` and `-h90.png`.
The roadmap manager passed them on 2026-10-19, judging frames for Aria that night; reopen it if they do not suit you.
**For Aria:** at the home heading the plant's name is stacked, POWER over PLANT, and at heading 90 the library's is on half its band, both because city hall stands in front; both are small, about 11 px at zoom 1, above the floor and readable, in case you want them bigger.
The release's demo set predates this and is re-filmed with the release.

**Aria's verdict** (2026-10-19, reviewing the frames the roadmap manager passed overnight): approved.
