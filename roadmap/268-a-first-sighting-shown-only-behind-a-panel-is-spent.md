# 268. A first sighting shown only behind a covering panel is spent, so it never shows

**Open. Filed 2026-10-26 (r1093), from item 264's session. Nobody's call — a defect.**

The city captions a kind of thing the first time it comes into view, once (`pkg/render/explain.go`, `queueSightings`; `explainCaptions` calls `scene.Sight`).
It calls `scene.Sight` whatever covers the map, so a sighting that happens while a notice, the board, the close-up, the settings, the breakdown, the timeline or the view key covers the city is drawn under the dim and marked seen.
Item 190's damaged-store frame shows one: the train's caption, under the notice's scrim.
Nobody can read it there, and it never comes again.

Item 168 already treats a first sighting nobody was shown as still owed when the city is shared; the same holds here.

## The fix

Hold sightings while anything covers the city — the same "covered" item 264 defines for hover — and caption them when the cover closes and the thing is still in view.
Tests, data-driven over the covers item 264 lists: a thing first seen under each cover is not marked seen; closing the cover captions it; a thing first seen with nothing covering is captioned at once, as now.
