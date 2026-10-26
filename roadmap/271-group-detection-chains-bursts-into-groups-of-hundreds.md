# 271. Group detection chains bursts of sessions into groups of hundreds

**Open, in progress since 2026-10-26 in the session "item 271". Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — a defect.**

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
