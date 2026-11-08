# 362. The demo film has no shot of the clinic's list, the action menu, the groups board or the keys

**Done 2026-11-07 (`c8cb3e8`, r1338). Filed 2026-11-07 (r1331), from item 360's audit of the website. Nobody's call — the shots are what shipped.**

Landed: slice 1 (`2d6695b`, r1333).
Landed: slice 2 (`6ad289a`, r1335).
Landed: slice 3 (`c8cb3e8`, r1338).

0.5.0's film (`make demo-media`, the scenarios in `botropolis/demo/scenarios/`) has no shot of:

- the clinic's list, opened with `a`;
- the action menu open, from `space` and from right-click, with a column's menu showing;
- City Hall's groups board, opened with `g`;
- every key drawn as a cap while `e` is held;
- City Hall at all: `pkg/city/landmarks.go` stands it only when the snapshot carries statistics (`if snapshot.Stats != nil`, lines 266–270 at `v0.5.0`), and the film's scenarios carry none, so no still has it. Give the film statistics, so the hall stands and the website can mark it.

The website (item 360) needs each one to show its Drive and Groups sections, and ships its text with the stills it has until the next film.

## The fix

Add each as a scenario shot, with a still and, where the move is the point (the menu opening, the board's rename), a clip, and give its caption the changelog's words.
Check them with `make check-demo-corpus`.

## Answered while building

- **Film them now, from 0.5.0** (Aria, 2026-11-07: *"Get the website fully up to date"*). The usual rule waits for a release to film, but this is filmed now for the website, which describes 0.5.0.
  So the shots are filmed from the `v0.5.0` binaries with the new scenarios, and only the shots that are new or changed, never a full re-film, and never from a build of `main` that holds unreleased work.
  They then go to [item 360](360-the-website-still-describes-the-city-of-0-3-0.md), which imports them into the site. The upload needs Aria's 1Password.
- **Shots for the website's Groups section** (Aria, 2026-11-07: *"I think we need an updated set of screenshots and videos for some parts of this site specifically groups"*). The Groups section has only the metropolis overview, the team clip and the tidy walk, and none shows 0.5.0's groups up close. Each shot below needs a still, and a clip where the movement is the point:
  - a neighbourhood inside its kerb, close enough to read;
  - the pointer on a grouped session, lighting its whole group while the rest fades (a clip, from pointing at nothing to pointing at it);
  - the group's line in each of `group_line_form`'s three forms, as three stills of one city;
  - moving a session into a group: the building fades out, the truck carries its crate, and it fades in on its new lot (a clip);
  - a teammate following its lead into a group, as a convoy (a clip);
  - closing a group from City Hall's board, packing its sessions into the depot (a clip).
- **The plan and test tree** (roadmap manager, 2026-11-07): approved. Slice 1 has the stager write `stats-cache.json` when a scenario sets `stats: true`, with tests in `pkg/demo` and the scenario integration test. Slice 2 adds the scenarios: `metropolis.yaml` gains statistics, and the new `controls.yaml` and `groups.yaml` are added.
- **All seven metropolis shots re-film** (roadmap manager, 2026-11-07). Adding statistics changes that scenario, which counts as "changed", and the site must not mix frames with and without City Hall.
- **The statistics come from the staged sessions**, not figures written to look like a heavy user (roadmap manager, 2026-11-07). The film shows what its own city did.
- **The city is 0.5.0's and the demo tool is main's** (roadmap manager, 2026-11-07). The `v0.5.0` tag's demo tool refuses the new `stats:` key, so `bin/botropolis` comes from the tag and `botropolis-demo` from the landed commit. That holds only if the diff between them touches nothing outside `pkg/demo`, `cmd/botropolis-demo` and `demo/`; the session checks this before filming.
- **Closing a group is filmed new, in `groups.yaml`** (roadmap manager, 2026-11-07), with 0.5.0's dialog. The site stops using the stale `tidy/close-group`.
- **What the hard stop checks** (roadmap manager, 2026-11-07): the tree that films. Every binary that films is built from `v0.5.0`'s tree, with only `pkg/demo` and `cmd/botropolis-demo` copied in from the landed commit. That tree's Go sources (`cmd/`, `pkg/`, `go.mod`, `go.sum` and `VERSION`) may differ from the tag only there, and `go list -deps` must show that `botropolis` and `botropolisd` import neither.
  This is stricter than comparing `v0.5.0` with `main`. Docs and tests never reach a binary, and `main`'s unreleased fixes, such as item 364's, never reach the film.
- **Moving a session into a group, and the convoy, come back from the release that fixes [item 365](365-a-hand-move-into-a-group-does-not-take-in-the-0-5-0-film.md)** (roadmap manager, 2026-11-07). In the film, 0.5.0 drops a move made by hand, whatever the group. The two shots are in `groups-moves.yaml`, which was left out of the 0.5.0 film and is filmed with 0.5.1's (item 366).
- **Filmed 2026-11-07** from `v0.5.0`'s binaries, with the demo tool from `6ad289a`. The hard stop held. Filmed: `metropolis.yaml` (all seven shots), `controls.yaml` and `groups.yaml`, 21 shots. In each metropolis still, City Hall's anchor is the only one added, and no other anchor moved by more than half a pixel.

## Closed

Landed in three slices.
Slice 1 (`2d6695b`, r1333) lets a scenario set `stats: true`, and the stager then writes `stats-cache.json` from the transcripts it staged, so City Hall stands. The metropolis sets it.
Slice 2 (`6ad289a`, r1335) adds `controls.yaml` and `groups.yaml`, and the scenario test now knows every landmark a script can aim at, with the hall only where it stands.
Slice 3 (`c8cb3e8`, r1338) puts moving a session into a group, and a team's convoy, in `groups-moves.yaml`.
The tests are `pkg/demo/stats_test.go`, `testing/integration/demo/scenarios_test.go` and `testing/acceptance/demo_test.go`.

It was filmed on 2026-11-07 from `v0.5.0`'s binaries, with the demo tool from `6ad289a`, into `botropolis/dist/item-362-film` (main checkout), with a contact sheet.
That is 21 shots: the metropolis's seven, re-filmed with the hall, and every shot of `controls.yaml` and `groups.yaml`.
[Item 360](360-the-website-still-describes-the-city-of-0-3-0.md) imports them.

**Deviation, for Aria:** the two move shots were not filmed. 0.5.0 drops a move made by hand ([item 365](365-a-hand-move-into-a-group-does-not-take-in-the-0-5-0-film.md)), so `groups-moves.yaml` was left out of this film and is filmed in 0.5.1's re-film, under [item 366](366-release-0-5-1.md).
Found on the way: a move into a team's group was dropped whatever else happened, which is [item 364](364-moving-a-session-into-a-team-s-group-is-dropped.md).
