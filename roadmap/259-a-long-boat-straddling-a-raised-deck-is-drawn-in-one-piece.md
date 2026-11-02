# 259. A long boat straddling a raised deck is drawn all in front of it or all behind it

**Fixed 2026-11-02 (`b53568e`, r1213). Filed 2026-10-26 (r1068), found by item 252's session from its frames. Nobody's call — a defect.**

Depends on: 252
Landed: slice 1 (`b53568e`, r1213).

[Item 252](252-the-second-bridge-is-too-low-for-the-liner.md) raised the second bridge's deck over the river so the liner clears it; its frames show the liner, longer than the deck is wide, straddling it: at 61% weekly usage its bow below the deck on the near side and its funnels behind it on the far side, drawn right.
At other readings it is drawn wrong: at 55%, mostly on the near side, a pier draws over its hull; at 64%, mostly on the far side, its stern draws over the deck's far edge.
The depth sort places a boat by one point, so a boat long enough to reach past both sides of the deck goes wholly before or wholly after it.
The taller piers item 252 brings make it plainer; the draw-order test it kept (a boat at the span's centre, every heading) holds a boat under the deck, not one whose ends reach past it.

## The fix

Draw a boat that straddles a deck in two pieces around it, cut where the deck's near and far edges cross the hull, each piece placed in the depth sort by its own point; a boat clear of every deck stays one draw, so the frame's draw count moves only while one straddles.

Tests: at readings that put the liner mostly near, centred and mostly far (55%, 61%, 64%), at every heading, no pier or deck pixel is drawn over the part of the hull in front of it and no hull pixel over the deck behind it; a boat clear of the deck is one draw; the night ceiling holds. Frames at those three readings for Aria.

## Answered while building

- **The couriers** (manager, 2026-11-02): cut the same way, since the fix is for a hull past a deck edge, not only for the liner.
- **The frames** (Aria, 2026-11-02): passed.

## Closed

Fixed by slice 1, two commits in botropolis: `b53568e` (r1213), the work, and `e209b74` (r1220), its line in the `[Unreleased]` changelog's Fixed section.
A hull reaching past a raised deck's edge is cut by screen column where each edge crosses its centreline, which is right at every height there and off by at most half the beam at the hull's sides,
and each piece sorts on its own stretch of the hull (`pkg/render/straddle.go`).
A boat clear of every deck edge is one draw, as before; the gauge boats and the refresh couriers both go through it.

Tests: `TestABoatStraddlingADeck` in `botropolis/pkg/render/straddle_test.go`, with the liner mostly near, centred and mostly far of the second bridge's deck and a courier at either edge, at every heading: one piece per side of each edge reached, the drawn columns taken once, the piece in front drawn after every deck part sharing its columns, the piece under before the spans over it, and the piece beyond before the deck; and a boat clear of the deck is one drawable.
The order checks went red with every piece on the old single point, on the first piece's footprint and on the last's,
and the column split and the edge range were mutated red too.
The night frame-work test held at 38.

**Deviation, flagged for Aria:** the test places the hull by geometry, its centre a third of its length toward the camera from the deck's centre, on it, or a third away (a courier at 0.4), rather than at 55%, 61% and 64%.
Where a reading puts the liner depends on the city's layout and flips with the heading; in the test's city, 61% at heading 0 is clear of the deck.

**Frames**, git-ignored in the item 259 worktree at `botropolis/dist/item-259/frames/`: `liner-55-4x.png`, `liner-61-4x.png` and `liner-64-4x.png`, 4x crops of the second bridge in a 17-district city at 2400×1350 by day, and the fit frames `liner-NN/overview.png`.
