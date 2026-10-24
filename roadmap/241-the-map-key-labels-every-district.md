# 241. The website's map key labels every district, where one would do

**Done 2026-10-24 (botropolis.city `fe99eff`, r1006). Filed 2026-10-24 (r1006) at Aria's request. Nobody's call — Aria ruled what it shows.**

Depends on: nothing
Landed: slice 1 (`3af74ef`, r1006).
Landed: slice 2 (`fe99eff`, r1006).

Aria, 2026-10-24, on the map key [item 231](231-the-website-still-talks-about-the-city-before-0-3-0.md) put live: *"We don't need to labe levery single directory on the glance. Just one of them with subtext to say that each plaza/district is a directory"*.
Item 231 gave each of the still's 12 districts its own hotspot, by name; that crowds the picture and says one thing twelve times.

## The fix

In botropolis.city's "Read it" section (`src/components/Glance.astro` and its data), keep one district hotspot and drop the other eleven.
Its line says that each district is a directory, quoting the app's own words (`pkg/city/kinds.go`: "a directory where sessions run"), as item 231's rule and test require.
Every other hotspot stays as item 231 left it.

Tests: `src/data/glance.test.ts`'s district cases become "it should have exactly one district hotspot" and "its line should say a district is a directory, in the app's words"; the placement, no-overlap and phone-scroll tests stay.
Then lint, test, push (CI deploys), `make verify`, and desktop and phone frames of the section for Aria.

## Answered while building

- **The one district hotspot** (manager, 2026-10-24, from Aria's ruling): titled "district", not a district's name, since its card speaks for all of them, and its line is `pkg/city/kinds.go`'s own sentence, *"Each district is a project: a directory on this machine. Its buildings are the sessions started there."*, on thistledown's plate, clear of the other hotspots. The test tree is approved as sent: exactly one district hotspot, its line saying a district is a directory in the app's words, the rest of `glance.test.ts` and the page tests unchanged.
- **Cards clipped at phone width** (manager, 2026-10-24, found by this session): at 360 px a card on the map's east side opens leftward from its spot and runs off the map frame's left edge, clipped, as every east-side card has since item 231. Fixed in this item as a second slice, since it is the same section: a card is clamped inside the map frame at every width, with a page test that each card, opened at 1440 and at 360, lies wholly inside the frame.

## Done

Two slices in botropolis.city, each deployed by CI on its push to `main` and checked with `make verify`:

1. `3af74ef` kept one district hotspot of twelve, titled "district", on thistledown's plate, its card quoting `pkg/city/kinds.go`: *"Each district is a project: a directory on this machine. Its buildings are the sessions started there."*
   `glance.test.ts` holds exactly one district hotspot, worded in the app's words; both cases were red first.
2. `fe99eff` keeps every card inside the map frame: when a card opens, or the map scrolls under an open one, it is moved sideways to sit 8 px inside.
   A page test opens each of the 12 cards at 1440 and at 360, its spot scrolled to the middle, and holds it wholly inside the frame; it was red on four cards at 360 (the road, river and district off the left edge, the depot off the right) and passes on all 24, locally and against production.

The frames went to Aria through the roadmap manager: the section at 1440 and 360, the district card open at both widths, and the road's card at 360.

**Aria's verdict**, 2026-10-24: *"Approve and close"*.

Deviations, flagged:
- The second slice was not in the item as filed; it was found while framing the first and added by the manager, since it is the same section.
- The card test's first version scrolled with the page's smooth scrolling, so the hover landed mid-scroll and all 12 cards at 360 failed on the right edge, a false red; it scrolls instantly now, and the red above is from that version.
