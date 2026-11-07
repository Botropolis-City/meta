# 361. The map's glossary still describes a group's stations, which 0.5.0 removed

**Open, in progress since 2026-11-07 in the session "item 361". Filed 2026-11-07 (r1331), found by item 360's session while reading the app for the website. Nobody's call — a defect.**

0.5.0's changelog says *"A group's line has no stations"*, but `pkg/city/kinds.go` at `v0.5.0` still carries `KindStation`: *"a project on a group's line"*, with the long line *"A group of sessions working on one thing is drawn as a line through its projects, with a station at each. A station's colour says whose move it is there."*
It is listed in the kinds' order (line 46), named as related by the session's entry (line 60), and named again on line 92.

## The fix

Remove `KindStation`, or, if anything still draws one, rewrite its entry as what is drawn now: the group's line between its districts and the link a pointer reads.
Move every `related` list that names it onto that kind instead, and add a glossary entry for the kerb, which has no wording in the app.
`kinds_test.go` and anything that walks every kind (the map key, the Keys panel and the hover cards) are what pin it now.
Item 360 quotes the app's own lines on the website, so it reads the new wording once this lands.

The website quotes the app's words and checks them live (item 360), so a rewrite here turns its check red where it quotes `KindStation`. Give the app a sentence that says what a group is, and tell the roadmap manager when this lands, so the site moves to the new words.

## Answered while building

- **Rename, don't delete** (roadmap manager, 2026-11-07). Nothing draws a station any more, but pointing at a group's line still returns a hit, so `KindStation` becomes `KindGroup`, with "group", "the sessions working on one thing" and the About the session proposed.
  A new `KindKerb` holds the kerb, which can't be pointed at.
  The project's and City Hall's related lists move to the group.
  The internal `StationHit` and `Station` types keep their names.
- **The line card says "site"** (roadmap manager, 2026-11-07), not "station". That matches the building card's "site 2 of 3" and 0.5.0's changelog, *"Pointing at a link shows what its station showed: the group, the site and the route"*.
- **The test tree** (roadmap manager, 2026-11-07): approved as proposed, in `pkg/city/kinds_test.go`, the line card test and `pkg/ui/explain_test.go`.
