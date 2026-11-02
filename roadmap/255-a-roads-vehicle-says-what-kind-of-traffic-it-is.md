# 255. A road's vehicle should say what kind of traffic it is, and no message should ride a group's line

**Done 2026-11-02 (`6c1726e`, r1223). Filed 2026-10-26 (r1056) at Aria's request, from item 105's frames. Nobody's call — Aria decided the mapping.**

Depends on: nothing

Item 105 filmed a real agent team for the first time: a lead in one district and its teammate in another, two messages between them.
With group lines off they ran as vans on the road between the districts; with them on, as red carriages along the group's straight line (`KindVan`'s reference sentence in `botropolis/pkg/city/kinds.go`: "Between two stations on a group's line, a carriage runs the line instead").
Aria, 2026-10-26, on the frames: *"I'm confused: first, why are trains running between the buildings directly? second they are just shooting diagonally not on any real track or road"*.
The carriages ride a line drawn over the city with nothing under them, and they look like the freight trains on the loop, which mean a model's spend, so one look carries two meanings.
And at the fit view a message van is hard to tell from a car, which means a session working across two projects right now.

Then, on what a road is for: *"the road should be drawn when we have a connection between two projects. The type of message should be conveyed by type of vehicle on the road (car, van, semi, truck, etc...)"*.

## What Aria decided (2026-10-26)

A road already appears only where traffic runs between two projects (`state.Road`); what runs on it says which kind:

| traffic on a road (`state.Road`) | vehicle |
| --- | --- |
| a session working in the other project right now (`Active`) | car, as today |
| a message one session sends another (`Messages`, `BackMessages`) | van, always on the road, never a carriage on a group's line |
| files a session edited in the other project (`Files`, `BackFiles`) | box truck |
| a subagent's visit across the pair (`Visits`) | motorbike |

The delivery truck that takes a merged pull request over the bridge stays as it is.
A group's line carries nothing; it stays a marker of who is grouped.

## The fix

1. Messages between sessions on a group's line drive the road as vans like any other; the carriage and everything that only it uses go, and `KindVan`'s reference sentence loses its second sentence.
2. Box trucks for files and motorbikes for visits, each spawned per unit of its traffic as vans are per message, with the hover card and the reference sentence for each new kind worded like the others in `pkg/city/kinds.go`, and the website's map key following at the release.
3. Every road vehicle reads as itself at the fit view and at full zoom: distinct in silhouette and size, not colour alone; item 134 set the train's scale against the cars, so the new vehicles take their sizes from the same scale.
4. The draw-count ceilings (`TestTheWorkAFrameTakes`) and the memory budget hold: new vehicles share the existing vehicles' batch.

Tests: for each kind of traffic on a road, the vehicle spawned is its kind, one per unit; a message between two stations on a group's line is a van on the road; nothing rides a group's line; each kind has its caption and reference sentence; the draw-count ceilings hold. Frames for Aria at fit and full zoom, by day and night, of a road carrying all four, and item 105's `team` scenario re-filmed.

## How it landed (2026-11-02, r1223–r1226)

- **What decided it** (manager, 2026-11-02): the Car Kit has no motorbike, and its own box truck is the pull request's delivery truck, so both new vehicles are modelled by hand in `botropolis/tools/render-sprites/buildings.py`, as the site trucks are. The box lorry is longer and taller than the delivery truck. A road's subagent visits are now counted each way (`state.Road.BackVisits`), so a motorbike leaves from the project that sent it. `city.Message` became `city.Traffic`, with a `Cargo` saying which vehicle it is.
- **What it does**: each message, file edited across and subagent visit sends its own van, box truck or motorbike along the road's street path, and each has its own caption, card and reference sentence. Vehicles leaving one way in one snapshot queue behind each other rather than stacking. The carriage on a group's line is gone, with its sizing, and `KindVan`'s second sentence.
- **Tests**: `TestRoadTraffic` in `pkg/city/traffic_test.go`, run for each kind of traffic. `TestRoadVehicles` in `pkg/render/roadvehicles_test.go` checks the box truck is at least a sixth longer, and the motorbike at most two thirds as long and half as wide, as any car, van or truck on the roads. `TestKinds`, plus a `BackVisits` case in `TestConnections`. `TestTheWorkAFrameTakes` held its ceilings in the landing gate.
- **Frames for Aria**: `botropolis/docs/screenshots/r1218-item-255-road-{fit,full-zoom}-{day,night}.png`, one road carrying all four (`botropolis-demo sheet --traffic`), and `r1218-item-255-team-{line,vans}.png`, the `team` scenario re-filmed with its shot `team-train` renamed `team-line`. They were filed as r1218 before a last rebase; the code they show landed as r1223.
- **For Aria to judge**: at the fit view every road vehicle is a speck, the new ones included, as the fit frames show; they are told apart at full zoom. botropolis.city's `src/data/media.json` still names `team/team-train` until the release refreshes it.
