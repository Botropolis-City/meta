# 259. A long boat straddling a raised deck is drawn all in front of it or all behind it

**Open. Filed 2026-10-26 (r1068), found by item 252's session from its frames. Nobody's call — a defect.**

Depends on: 252

[Item 252](252-the-second-bridge-is-too-low-for-the-liner.md) raised the second bridge's deck over the river so the liner clears it; its frames show the liner, longer than the deck is wide, straddling it: at 61% weekly usage its bow below the deck on the near side and its funnels behind it on the far side, drawn right.
At other readings it is drawn wrong: at 55%, mostly on the near side, a pier draws over its hull; at 64%, mostly on the far side, its stern draws over the deck's far edge.
The depth sort places a boat by one point, so a boat long enough to reach past both sides of the deck goes wholly before or wholly after it.
The taller piers item 252 brings make it plainer; the draw-order test it kept (a boat at the span's centre, every heading) holds a boat under the deck, not one whose ends reach past it.

## The fix

Draw a boat that straddles a deck in two pieces around it, cut where the deck's near and far edges cross the hull, each piece placed in the depth sort by its own point; a boat clear of every deck stays one draw, so the frame's draw count moves only while one straddles.

Tests: at readings that put the liner mostly near, centred and mostly far (55%, 61%, 64%), at every heading, no pier or deck pixel is drawn over the part of the hull in front of it and no hull pixel over the deck behind it; a boat clear of the deck is one draw; the night ceiling holds. Frames at those three readings for Aria.
