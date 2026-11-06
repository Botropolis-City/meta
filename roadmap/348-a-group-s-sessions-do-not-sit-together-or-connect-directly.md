# 348. A group's sessions do not sit together, and its line does not connect them directly

**Open, in progress since 2026-11-06 in the session "item 348". Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Aria's call — which of the three forms below, on frames.**

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
