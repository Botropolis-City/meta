# 271. Group detection chains bursts of sessions into groups of hundreds

**Open, in progress since 2026-10-26 in the session "item 271". Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`28f4360`, r1106).

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
