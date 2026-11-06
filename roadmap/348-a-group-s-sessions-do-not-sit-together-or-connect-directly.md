# 348. A group's sessions do not sit together, and its line does not connect them directly

**Done 2026-11-06 (`93cbf78b`, r1297). Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Aria's call — which of the three forms below, on frames.**

Depends on: nothing
Landed: slice 1 (`a980c7a2`, r1291).
Landed: slice 2 (`c171d398`, r1294).
Landed: slice 3 (`f1154861`, r1293).
Landed: slice 4 (`93cbf78b`, r1297).

Aria, on a group whose three sessions in one district showed badges and no line: *"We should make group lines draw between sessions in the same district and they should not go to districts themselves just directly from session to session. Also, buildings in the same group should try to group into neighborhoods (like sit together) If we nail that, maybe we will only need it between buildings in different disricts. or we can circle them with a line like a neighborhood instead of floating on top and then connect neighborhoods."*

## Where it stands

- **No line inside a district.** `Line.Leads` in `pkg/city/lines.go` keeps a line only if its stations are in more than one district, so a group in one district has badges and nothing else.
- **A line's stops are stations, not buildings.** `City.station` puts each one at the average of the group's buildings in that district, nudged sideways per line, so it usually floats beside them, on nothing.
  It stands at a district's centre only for a district where the group has no session and the coordinator's subagents worked.
- **Group members sit wherever they landed.** `Layout.Slots` gives each session a sticky slot in its district's grid, in the order they arrived (`pkg/city/layout.go`), and nothing looks at groups.
  A group's buildings are scattered among the others.
- **The lines float over the city by ruling.** Aria dropped item 179 on 2026-10-20, after drawing the line on the ground was built and judged on frames.
  A neighbourhood's outline is a new shape, so that does not settle it, but anything on the ground should be judged knowing it was tried.

## What it wants

**First, neighbourhoods.** A group's buildings in a district try to sit in adjacent lots.
Everything else reads differently once this exists, so it comes first.

**A neighbourhood is recognisable by itself.**
Aria: *"It'd be like how you can recognize chinatown in almost any big city in the us"*.
The point taken from that is recognition, not that style: you know where you are from the place's own character, before reading a sign or following a line.
So the test of a neighbourhood is whether you can spot a group on the map with no line and no badge.
Sitting together is the start of it, and the rest is something the group's buildings share, such as a gate or marker at its edge, a shared ground or street treatment, or a common trim.
It has to stay out of what already means something: a building's height, lights and tones carry its state, and [the colour rule](../botropolis/rules/why-the-category-colours-are-legal.md) limits what a new colour may be.
Any new art follows [the art sources rule](../botropolis/design/art-sources.md).
If this works, the second and third forms below need much less drawing.

**Then one of three forms, picked on frames of the same city:**

1. **Session to session everywhere.** The line runs building to building, in a district and between districts, with no stations.
2. **Only between districts.** Sitting together is what says "group" inside a district, and the line runs directly between buildings only across districts.
3. **Neighbourhoods and links.** An outline circles each neighbourhood, and one link joins neighbourhoods across districts.

The recommendation is the third.
A group with 16 sessions in two districts would need at least 15 segments under the first form, over buildings that already carry a team's dashed lines to their lead (item 343 puts a whole team in one group, so those overlap exactly).
The third draws two outlines and one link for the same group, and it does not depend on the order of the sessions.

## Decided

**A building moves when Aria changes it, and the move is drawn** (Aria, 2026-11-05): *"buildings should move if I make a change to them. And the move should be a visible animation so I don't lose track of things."*
So moving a session into a group, or out of one, carries its building to its new lot where she can watch it go.
A session keeping its lot stays the rule otherwise, since `Layout.Slots` and `design/city-and-rendering.md` rely on it: a guess by the detector does not move a building.
Packing already drives its crate to the depot (`pkg/city/haul.go`), which is the precedent to start from, and under reduced motion a building fades in where it lands, as packing does.
With item 343, moving a lead moves its team, so several buildings move at once and each has to stay trackable.

## What has to be decided while building it

- **What stations carry.** A station is more than a dot: it shows whose move each site is, its card says "station 2 of 4", it holds what a site waits on (item 90), and a pull request opened outside the group is a stop of its own.
  The chosen form has to keep these somewhere, or say which are dropped.
- **A stop with no session.** A district only the coordinator's subagents worked in has no building to connect to.
  This ask says lines do not go to districts, so it goes, or becomes something else.
- **One session on the map.** Item 344 shows the group; a neighbourhood of one is an outline around one building, or nothing.
- **Cost.** The lines are a cached layer of their own (`design/what-it-costs.md`); building-to-building lines move with the buildings' lifts and the budgets in `performance/` apply.
- **The City Plan.** It draws lines too (`pkg/city/cityplan.go`), and whichever form wins has to mean something there.

## Slices

1. Neighbourhoods: slots that keep a group adjacent, with the drawn move decided above, and tests that a group's buildings are neighbours, that a move by hand animates, that a detector's guess moves nothing, and that an unrelated session keeps its lot.
2. What makes one recognisable, tried on frames with no lines drawn.
3. Frames of all three forms on one staged city and on a large one, for Aria.
4. The form she picks, and everything the old stations did moved or retired.

Every one of them needs a frame for Aria, since this is how the map looks.

## Answered while building

- **Slice 1's test tree** (roadmap manager, 2026-11-06): approved as sent — `Layout.Slots` places an arrival on the free lot nearest its group, re-slots a session only when its group was changed by hand and records the group each lot was chosen for, so a rebuild moves nothing; `group.Result.Moved` and `Session.GroupMoved` carry "by hand" from the detector; the move is a third haul kind, `HaulMove`, at the truck's speed with the building riding the truck, staggered as a convoy, and a 300 ms fade-in under reduced motion.
  The building riding the truck is a drawing choice, so it comes to Aria on a frame.
- **A re-flow of the grid does not re-pack neighbourhoods** (roadmap manager, 2026-11-06, from Decided above): when a district's grid widens, every building shifts as it does today and the recorded lots stay, since nobody changed those sessions; whether a neighbourhood should re-pack is judged on slice 3's large-city frames.
- **A take-out is a change by hand** (roadmap manager, 2026-11-06, from Decided above): a session taken out of a group leaves its neighbourhood, and if the detector then holds it in another group it moves beside that one, once, at Aria's action; a later change of the guess moves nothing.
- **Slice 1, as built** (item 348's session, 2026-11-06): a take-out reaches the city through `group.Result.TakenOut` and `Session.GroupLeft`, since it leaves no move on the session; the "moved to none, then guessed elsewhere" case is skipped with its reason, since a session moved to none sits out detection, and the taken-out version runs; the truck is drawn in front of the building it carries.
- **Slice 2's test tree** (roadmap manager, 2026-11-06): approved — three treatments tried on frames with no line and no badge, each only for two or more buildings in a district: shared ground paving the gaps between a group's adjacent lots, a kerb round the block's outside, and a gate post at the corner nearest the district's driveway; no new colour, shapes from Go or the kits already in the atlas.
- **The gate's name** (roadmap manager, 2026-11-06): framed both ways for Aria, who picks; the recognition test is the frames with no name, since the item asks that a neighbourhood be known before reading a sign.
- **The move carries a crate** (Aria, 2026-11-06, on slice 1's frames): *"Use a crate, as packing does"* — a building riding its truck read as a building with a car parked in front, so the truck carries a crate as packing's does, the building fading out at its old lot and in at its new one.
- **The kerb is the mark, made stronger** (Aria, 2026-11-06, on slice 2's frames): of shared paving, a kerb and a gate, only the kerb showed, and too thinly behind tall buildings; it stays and is made to read past them, and the paving and the gate are dropped.
- **A session in no group keeps room for groups** (Aria, 2026-11-06): it takes the first free lot that borders no group, and any lot only when none is left; nothing already placed moves.
  This changes slice 1's "a session in no group takes the first free lot".
- **Slice 3's test tree** (roadmap manager, 2026-11-06): approved — a trial `LineForm` on the scene, stations the default; session to session chained in site order, only between districts joined at the nearest pair of buildings, and neighbourhoods and links outlined with block-centre links; a site with no session skipped by all three; no stations drawn in a form, since what they carry is slice 4's question.
- **Round two, built** (item 348's session, 2026-11-06): the move carries a crate and puts up no scaffolding on the way; the kerb is a low raised wall in the lines' ink, cased in their dark, tried on the ground (partly hidden by buildings in front) and over the city as lines are (reads past every building), raised being the default until Aria picks; a loose session takes the first free lot bordering no group.
  The form frames are re-shot with the kerb off, so each form's shape is the only difference between them.
- **The kerb is on the ground** (Aria, 2026-11-06): *"On the ground"* — partly hidden by the buildings in front of it, rather than drawn over the city as the lines are.
- **The form is not picked yet** (Aria, 2026-11-06): leaning to neighbourhoods and links, she asked to see the four forms with the kerb on the ground, *"with and without the group being hovered (so non-group buildings disappear a little)"*, eight frames on the large city.
- **The form: only between districts by default, the others as settings** (Aria, 2026-11-06, on the eight frames): *"This is a hard decision. But I think I have a solution. Let's make districts the default and allow neighborhoods and all session to session as settings"*.
  So slice 4 makes "only between districts" the default — the kerb says "group" inside a district, and one line joins the nearest buildings across districts — and "neighbourhoods and links" and "session to session" become the other values of one setting, beside `group_lines`, reachable from the settings panel; stations go.
  What stations carried (whose move each site is, its place in the line, what it waits on, a pull request outside the group) is slice 4's to keep somewhere or name as dropped, for every value of the setting.
- **Where what stations carried goes** (item 348's session, 2026-11-06; the drops accepted by Aria the same day): the line and its sites stay as data, feeding the stand-up, the dive, the board and the cards, and only the drawn station dots go; `group_line_form` (`districts` by default, `neighbourhoods`, `sessions`) sits beside `group_lines`.
  Off the map, with Aria's acceptance: whose move each site is (each building's tone and the district sign still say it), a pull request opened outside the group (kept in the dive and the stand-up), the site office and the line's label (the coordinator's card and every member's badge keep them), and a district only the coordinator's subagents worked in (kept in the dive and the stand-up).
  Kept: a building's place in the line, as "site 2 of 4"; a waiting site's link drawn unlit, its "waits on…" on the cards of the buildings there; a guessed site's link dashed; hovering a link or an outline shows the line's card; a dragged building dropped on a link or a group's building joins that group; a hovered car's districts keep their links lit; the City Plan's lines run badge to badge without dots; a group in one district draws no line in `districts`.
- **Slice 4, as built** (item 348's session, 2026-11-06): `group_line_form` beside `group_lines`, `districts` by default; no stations drawn; a link under the pointer answers as its site's station did, so the card, a drop on it and a hovered car's lit districts carry over; a form change re-shapes the lines at once, the lines' cache key naming the form; "site 2 of 3" in place of "station 2 of 3".

## Closed

Done in four slices, landed together as r1287 to r1297 (`70af5a42` to `93cbf78b`).

- **Neighbourhoods** (slice 1): a session with no lot takes the free one nearest its group's, and a loose newcomer takes one that borders no group while the grid has one.
  A move by hand, into a group, out of one or a take-out, carries the building across: it fades out at its old lot, a truck carries its crate as packing does, and it fades in at the new one, a convoy for a team.
  A guess moves nothing, and the layout records the group each lot was chosen beside, so a moved building sits still afterwards.
  Tests: `TestNeighbourhoods`, `TestMoves`, `TestMoved`, `TestTakenOut`, `TestLoaderGroupMoved`, `TestLoaderGroupLeft`.
- **The mark** (slice 2): a raised kerb in the lines' ink round each neighbourhood of two or more, on the ground, partly hidden by the buildings in front ("On the ground").
  The paving and the gate were dropped on frames. Tests: `TestNeighbourhoodBlocks`, `TestNeighbourhoodEdges`, `TestKerbWall`, `TestKerbsKey`.
- **The forms** (slices 3 and 4): `group_line_form`, `districts` by default, `neighbourhoods` and `sessions`, in the settings panel beside group lines and in botropolis-config(5); stations are no longer drawn, and what they carried is where the list above says.
  Tests: `TestLineForms`, `TestLinkHover`, `TestLineFormSetting`, `TestGroupLineFormKey`, `TestGroupLineFormSettingsRow`, and "when the line form changes" in `TestKeepingTheGroupLines`.

Frames, not committed, sent to the roadmap manager for Aria: the default form on the large staged city plain, with API focused, with API under item 359's real hover, and the settings row.

Deviations, flagged:
- A link under the pointer answers with the existing station hit, pointing at its site, rather than a new kind of hit, so the card, the drop and the car-lit districts carried over unchanged.
- The large city was staged in code, not from the metropolis scenario, because the command line could not carry the trial settings.
- At the fitted view, item 359's dim under a group hover reads modestly; a close-up frame shows it working. Strengthening it is item 359's.
