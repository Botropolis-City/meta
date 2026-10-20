# 155. A building's windows should light as each part of it is finished

**Done 2026-10-19 (`5954bc5`, r781). Filed 2026-10-19 (r780) at Aria's request, from item 74's frames.**

Depends on: nothing
Landed: slice 1 (`5954bc5`, r781).

[Item 74](074-night-glow-discs-are-back-in-the-demo-frames.md) (`a945b61`, r779) stopped night glow being drawn over buildings that aren't standing, and lights a new building only at the end of its build (`Site.Lights`, 0.88–1).
Aria, 2026-10-19, judging its frames: *"Any part of the building that is done should light up (when expected). All I see in this PR is some glow rings being removed from assets that have a lot with no building."*

## The fix

- **Floor by floor:** during a build, a storey's windows light (at night, as standing buildings' do) once that storey is built, so a building lights from the ground up as its floors rise; scaffolding and the floor being built stay dark. The same for a compaction's new course, an upgrade's new storey and a spire segment, wherever the city builds part of a building.
- **Frames that show it:** night frames where buildings are actually lit, not only empty lots gone dark: a standing lit district, and a build at night stepping through its floors lighting one by one. If item 154's start-up fix (live sessions no longer sail in at open) hasn't landed, stage the scene so the buildings stand.

Tests: a building mid-build should light exactly its finished storeys; the storey under construction should be dark; a finished building lights every storey; no light is drawn above the built height (item 74's guard holds).

## Done

**Each storey's windows now light once that storey is built.**
`windowRows` lights every storey whose top the rising building has reached, at its full-size height, so a building lights from the ground up, the storey still going up stays dark, and nothing is lit above its roof.
`Scene.Lights` is on through a build wherever floors are finished, and still off while the tug sails or a truck carries the building (item 74's guard).
The daytime look is unchanged: `Site.Lights` still brightens the sprite as the scaffolding comes down.
Tests are in `pkg/render/glow_test.go` (`TestWindowRows`) and `pkg/city/construction_test.go`; the two guards, the storey under construction stays dark and no row is above the built height, were each mutated red.

**The night glow also sits on the building's own storeys now.**
It used to invent its storeys from the sprite's height (one per 38 px), so its rows did not match the building's storeys.
A city kit building now uses its session's storeys, so an upgrade lights its new storey the moment the building gains it, while the storey being built on its roof is scaffolding and stays dark.

**Nothing new for courses or spires**, by the manager's ruling: a compaction's course has no windows and already glows while it is new (item 109), and a spire has no windows, only its beacon.

Frames, at r782 (`aa8c3dc`), filmed at 22:30 from the demo corpus once the start-up arrivals had finished building: `botropolis/docs/screenshots/r781-item-155-lit-city.png`, the whole city standing and lit, and `botropolis/docs/screenshots/r781-item-155-build-at-night.png`, one arrival beside lit neighbours, from docked (nothing lit) through the ground floor lit with the second rising to standing with both floors lit.
They are cited as paths because the main botropolis checkout had not pulled them when this closed.

**For Aria:** a storey's windows switch on when it is finished rather than fading in.
