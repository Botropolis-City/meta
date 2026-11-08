# 364. Moving a session into a team's group is silently dropped

**Open, in progress since 2026-11-07 in the session "item 364". Filed 2026-11-07 (r1333), found by item 362's session while test-filming 0.5.0. Nobody's call — a defect.**

Moving a session into a group that a team makes, by hand from *move to group*, does nothing.
The picker says "moved to <group>" and the session stays where it was.

## Where it stands

In `botropolis/pkg/group/cluster.go`, `place` runs `placeMoved` before `followLeads`, at line 80 and line 82 at r1333.
A team's group exists only after `followLeads` has made it, which [item 343](343-a-teammate-is-not-always-in-its-lead-s-group.md) built.
So when `placeMoved` runs, `groupFrom` finds no group with the move's id and skips the move.
When that group is also stored in memory, it is worse: `Detect` returns two groups with one id, one holding only the moved session and the other holding the team.

Repro: a lead and a teammate in team "crew", a third session `c`, and `Memory{Moves: [{c, <the team group's id>}]}`.
Then `Detect` leaves `c` out of the team's group.

## The fix

Place the moves after the teams have formed their groups, or let `placeMoved` create the team's group, so a move into it lands.
And never let `Detect` return two groups with one id: a test across `place`'s orders should hold that.
Tests in `pkg/group`: when a session is moved into a team's group, it should be a member of that group; and when that group is also stored, there should be one group with that id.
Moving the lead out still carries its team, as 343 rules.
Item 362's film moves sessions into a group that isn't a team's, so the film doesn't show this bug.

## Answered while building

- **The fix and test tree** (roadmap manager, 2026-11-07): approved. `place` splits in two. A lead's moves and starts run first, so a moved lead still carries its team (343). Then `followLeads` runs, then everyone else's moves and starts. A guard keeps `teamGroup` from making a second group under an id already in the result.
  The tests sit in `teams_test.go`, and a generated `unique_test.go` (seeds 1–200) checks that no two groups ever share an id.
- **A session started from a team's group is fixed here too** (roadmap manager, 2026-11-07). It is the same order defect, entered through `joinStarted`.
- **The changelog line** (roadmap manager, 2026-11-07), under Fixed, covers both doors: moving a session into a team's group, or starting one from it, puts it there.
- **The generated test runs 1,000 seeds, not 200** (roadmap manager, 2026-11-07, approving the session's change). A second way to get two groups with one id, unrelated to the order, first shows at seed 397. Detection takes a stored group's id, and a lead with no free stored group then made a fresh group under `newID(lead)`, which is the same id.
  The `freshID` guard fixes it: a fresh group never takes an id already in the result or in memory. With the guard off, 6 of the 1,000 seeds fail.
