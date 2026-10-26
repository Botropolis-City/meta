# 271. Group detection chains bursts of sessions into groups of hundreds

**Fixed 2026-10-26 (`b3bce70`, r1112). Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`28f4360`, r1106).
Landed: slice 2 (`b3bce70`, r1112).

On that laptop the detector made 48 groups, seven of them with 61 to 781 members.
A group is a set of sessions working together; nobody runs 781 sessions together.

## Why

`pkg/group` scores pairs (`cluster.go`), and a start within a minute of another session's start or close (`together`, `detect.go`) is *Likely* on its own, and Likely is enough to join.
`cluster()` then chains joins transitively, so any steady stream of sessions — scripted `claude -p` runs, a test suite that starts Claude, a busy afternoon — links into one group, minute by minute.
`state.applyGroups` (`pkg/state/groups.go`) feeds every session in the snapshot to it, not only those in the 30-day window.
Item 223 met the same chaining in the staged metropolis and fixed the staging only, with no detector change.

## The fix

- Timing alone never joins: a start near another start or close only supports a pair that some other evidence (a shared directory, a team, a message, a parent) already ties.
- No transitive chain through timing: a group is held together by its strongest evidence, not by a path of minute-apart neighbours.
- A bound on what one group can be, with the evidence that would exceed it logged rather than drawn.
- Tests: a stream of 500 unrelated sessions a minute apart makes no group; two sessions with real evidence and close timing still group; the existing group tests stay green; and a staged history like item 270's makes no group above the bound.

## Answered while building

- **Timing alone** (Aria, 2026-10-26, asked by the manager): starting together only suggests a group; it joins only beside other evidence, never chains, and the two existing cases that held a minute-apart pair as a join become suggestions. This supersedes her earlier ruling that a minute-apart start joined as likely.
- **The bound and directory evidence** (manager, 2026-10-26): no group takes more than 40 members, a named constant, with refused joins logged; directory evidence means subagents working in the other's directory and shared files, with no new same-directory signal, since a stream of scripted runs in one directory would chain again.
- **The demo scenarios that grouped on timing alone** (manager, 2026-10-26): `team` plays its timeline to the end before its groups are checked, so its pair groups on the replayed team and message; `workday` and `workshop` give each staged pair a shared feature branch through a new `branch:` overlay, an honest second weak signal beside starting together, which keeps item 223's badge and station checks. New session's guess for a group you were in a minute ago reads *perhaps* rather than *likely*, and still picks the same group.
- **A key shared by more sessions than a group holds** (manager, 2026-10-26, from the wording code's own rule for a too-common word, and since an arbitrary 40 of 800 is a group nobody formed): it is not evidence. The candidate index stops pairing sessions on it, and the daemon logs it once; pairs that also share real evidence still group on that. Slice 2 cuts the first load's scoring this way, counted deterministically on item 270's shape.

## Closed

Slice 1 (`28f4360`, r1106) took timing out of every join it made on its own.
A pair that needs its timing to be likely is a timed edge, taken after every other, and it joins only one hop from evidence, so timing never chains.
No detected group takes more than `group.MaxMembers`, 40; a session refused by a full group joins none and is in `Result.Capped`, which the daemon logs when it changes.
Slice 2 (`b3bce70`, r1112) stopped treating a reference, team, branch or file that more than 40 sessions share as evidence, which takes the scoring cost out of the first load: on 2,400 synthetic sessions with 800 sharing one key, the ties kept fell from about 345,000 to 28,500.

What shows it, in `pkg/group`: `timing_test.go` (500 unrelated sessions a minute apart make no group; real evidence beside close timing still groups; a stream tied by files and timing stays in pairs; a session tied by timing only to a member that joined on timing stays out), `bound_test.go` (a staged history at item 270's scale, 1,600 sessions in 600 directories, went from one group of all 1,600 to its ten real groups, none above the bound), `common_test.go` (common keys, and the incremental detector agreeing with a fresh one when a key crosses the bound), and `pkg/state/groups_bound_test.go` for the two log lines.

Deviations, each settled with the manager and listed above: two existing cases that joined on a minute-apart start are suggestions now; New session says *perhaps* for a group you were in a minute ago; and the team, workday and workshop scenarios got real ties, which changes when the team-train shot's line appears and adds a branch to two cards in workday and workshop.
Those demos are re-filmed in 0.3.3.
Not changed: `state.applyGroups` still hands detection every session in the snapshot, not only the 30-day window, since the fix needed no window, and items 272 to 274 take most of those sessions off the map.

