# 371. The demo film cannot show a move taking

**Open. Filed 2026-11-07 (r1343), found by item 366's session in 0.5.1's re-film. Nobody's call — a defect in the film tooling.**

`demo/scenarios/groups-moves.yaml`'s two shots, `move-in` and `convoy`, film a session being moved into a group. At 0.5.1 (`a9bfaad7`) the notice says "moving to kiln…", but the building never moves, and sixteen seconds later the stream still has only that line.
The move itself works: 0.5.1's live checks saw it take in 83 ms on a quiet home and in 147 ms on a real one ([item 366](366-release-0-5-1.md)).

## Where it stands

A city run with `--headless`, `--record` or `--script` works in a private temporary copy of the state directory: `notOwnCity` in `pkg/app/module.go` calls `statedir.MakePrivate`, which item 114 added.
That keeps a filmed or scripted city from touching the real state, but its move writes `groups.json` into the copy, and the shot's daemon reads the real one, so the move never reaches it.
The film runs every city that way.

## The fix

Let the film's city and its daemon share one state directory that belongs to the shot, not to the person. Do it through a flag or the scenario's `daemon: true`, never by turning off item 114's protection for a person's own cities.
Test it in `pkg/app`: a recorded city given the shot's state directory writes its moves there, and one without it still writes to a private copy.
Then film `groups-moves.yaml` from the next release, and [item 360](360-the-website-still-describes-the-city-of-0-3-0.md) adds its two clips to the site's move cards.
