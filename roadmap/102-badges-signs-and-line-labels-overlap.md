# 102. Group badges, district signs and line labels draw over each other

**Fixed 2026-10-18 (`5b304e9`, r628). Filed 2026-10-17 (r549) at Aria's request, from a frame of item 100's. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`cf1306e`, r616).
Landed: slice 2 (`fa44392`, r624).
Landed: slice 4 (`5b304e9`, r628).
Landed: slice 5 (`21e02b9`, r630).
Landed: slice 3 (`6fe8816`, r631).

In `botropolis/docs/screenshots/r541-item-100-1600.png`, a fitted 1600 by 900 view of the workday demo, several buildings carry three labels in one spot: a group badge ("lanternfish"), the district's sign on its post, and the group line's station label.
They are drawn over one another, so none of them can be read; around the middle of the frame, two "lanternfish" plates cover a district board.

## Where it comes from

Each is placed on its own, with no knowledge of the others:

- the badge, `badgeLayout` in `botropolis/pkg/render/badge.go`, is centred `badgeDrop` below the building's foot (item 87);
- the district sign, `districtSign` in `botropolis/pkg/render/districtsign.go`, stands its board on a post above the district's front corner (item 88, capped by item 98);
- the line's station label is drawn beside its station, which stands among the group's buildings (item 87, slice 4).

All three are called from `drawIso` in `botropolis/pkg/render/iso.go`, so that is where they can be made to know about one another.

## The fix

Lay the labels out together, after the buildings are placed: collect each label's rectangle, give the district sign the right of way, and step a badge or a station label aside, down, or out to a short leader, when it would cover another.
Where there is no room, the lower-priority label is left off at that zoom, as the sign already is below its floor.

Tests: a pure layout over rectangles, data-driven over the collisions in the frame — badge on sign, two badges, station label on badge — that no two drawn labels overlap and the district sign never moves; and a frame at 1600 of the same scene for Aria.

## Aria's rules for labels (2026-10-17)

From a clip of item 89's, where a district sign covered a drone: *"We should do proper perspective. Real signs that are part of the map should be either in front of or behind the drone depending where the drone is… That said, labels that are not real things on the map. like informational labels or floating name labels and such, those should almost always be drawn over real things unless the label is like clearly far back and the perspective would be bizarre. Also, we should be able to turn on and off all labels with a hotkey."*

- **Real things are depth-sorted**: a district sign on its post is part of the map and sorts with buildings, cars and drones. Item 89 puts drones and signs in that sort.
- **Labels are not real things**: badges, floating names, station labels and tooltips draw over the world, except where a label is clearly far behind what covers it and drawing it on top would look wrong. This item lays them out together so they do not cover one another.
- **A hotkey turns every label off and on**, as a setting beside the others, so the map can be looked at bare; real signs stay, because they are part of the map.

## Answered while building

- **The layout** (manager, 2026-10-18): badges, station labels and district signs are laid out together in their own file, and badges and station labels draw after the depth pass, over the world; right of way runs sign, then station label, then badge, the front-most badge first; a badge moved past its first ring of neighbours carries a leader back to its building, and one boxed in on every side is left off. The floating plate that stands in for a sign too small to read keeps a sign's right of way, but is an informational label: it draws over the world and the hotkey hides it, while the real sign on its post stays.
- **The hotkey** (manager, 2026-10-18): `z`, configurable like the other keys, with a settings row "labels: shown / hidden"; `h` still hides the whole interface. Slice 1's tree was approved, with an acceptance test that cannot pass on an empty frame.
- **What `z` hides** (manager, 2026-10-18): badges, station labels, street labels, landmark plates and the floating district plate, through one switch in the scene; signs on posts and paint on buildings stay, and a hover card stays, since pointing asked for it. The key and the settings row share one save, so they cannot disagree. Slice 2's tree was approved.
- **The floating plate gives way to its own sign** (item 102's session, 2026-10-18): it is placed first among labels, but steps aside for a real sign rather than covering it, since hovering a district whose sign shows had put the plate on its own board.
- **Slice 4** (`5b304e9`, r628): road tags and first-sighting captions join the layout and hide with `z`; with a car hovered, labels outside its highlight fade while its districts' labels and its road's tag stay, as Aria asked. A slice 2 bug — the floating plate drawn where it asked even after being stepped off a sign — was on main from r624 to r628. Aria asked that the cost of laying out every label each frame, and of moving road tags out of the cached static layer, be measured before closing.

## Closed

Fixed 2026-10-18; Aria passed the frames ("Pass, close it").
Every label the map draws is now laid out together each frame, in `botropolis/pkg/render/labellayout.go` and `maplabels.go`: a district sign never moves, then the floating plate and a first sighting's caption, then station labels, badges front-most first, and roads' traffic tags last; a label that would cover another steps down or aside, further out on a leader, or is left off.
Labels draw over the world, `z` and the `labels` row hide them all while signs on posts stay, and with a car hovered every label outside its highlight fades.

- Tests: `TestLayoutLabels`, data-driven over the collisions, and `TestLabelsDoNotOverlap` on the workday and workshop demos, which must find each kind and was red on the old placement; `TestLabelsHotkey`, `TestLabelsKey`, `TestLabelsHidden` and `TestLabelsFadeWithTheHighlight`.
- Frames, at r630: `botropolis/docs/screenshots/r630-item-102-workday-1600.png`, `r630-item-102-workday-1600-labels-off.png`, `r630-item-102-workshop-1600.png` and `r630-item-102-workshop-1600-car-hover.png`.
- Cost (slice 5, `21e02b9`, r630): the layout alone takes about 7 µs for the 42 labels metropolis shows close up, 0.15 ms for 200 and 1.9 ms for 800, so it is left uncached; whole metropolis frames before and after slice 4 differ by less than the noise. `BenchmarkDrawAFrame` and `BenchmarkLayoutLabels` run in the release's benchmarks.
- Beyond what the item asked, flagged for Aria: road tags and first-sighting captions joined the layout (slice 4, at the manager's ruling), and holding `e` still captions everything over the map, unlaid.
