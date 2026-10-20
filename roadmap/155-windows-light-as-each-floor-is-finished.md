# 155. A building's windows should light as each part of it is finished

**Open, in progress since 2026-10-19 in the session "item 155". Filed 2026-10-19 (r780) at Aria's request, from item 74's frames. Nobody's call.**

Depends on: nothing

[Item 74](074-night-glow-discs-are-back-in-the-demo-frames.md) (`a945b61`, r779) stopped night glow being drawn over buildings that aren't standing, and lights a new building only at the end of its build (`Site.Lights`, 0.88–1).
Aria, 2026-10-19, judging its frames: *"Any part of the building that is done should light up (when expected). All I see in this PR is some glow rings being removed from assets that have a lot with no building."*

## The fix

- **Floor by floor:** during a build, a storey's windows light (at night, as standing buildings' do) once that storey is built, so a building lights from the ground up as its floors rise; scaffolding and the floor being built stay dark. The same for a compaction's new course, an upgrade's new storey and a spire segment, wherever the city builds part of a building.
- **Frames that show it:** night frames where buildings are actually lit, not only empty lots gone dark: a standing lit district, and a build at night stepping through its floors lighting one by one. If item 154's start-up fix (live sessions no longer sail in at open) hasn't landed, stage the scene so the buildings stand.

Tests: a building mid-build should light exactly its finished storeys; the storey under construction should be dark; a finished building lights every storey; no light is drawn above the built height (item 74's guard holds).
