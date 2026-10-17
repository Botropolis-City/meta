# 102. Group badges, district signs and line labels draw over each other

**Open. Filed 2026-10-17 (r549) at Aria's request, from a frame of item 100's. Nobody's call — a defect.**

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
