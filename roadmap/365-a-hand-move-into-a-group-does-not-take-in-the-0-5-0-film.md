# 365. A hand move into a group does not take in 0.5.0's film

**Open, in progress since 2026-11-07 in the session "item 365". Filed 2026-11-07 (r1333), found by item 362's session while test-filming 0.5.0. Nobody's call — a defect, cause not yet known.**

In the demo film, with the city on `v0.5.0` and `daemon: true`, *move to group* into any group says "moved to <group>", and the stream logs it, but the session never joins.
Ten seconds later its card has no group line, and its menu still offers *move to group* instead of *take out of group*.
Two moves seven seconds apart both failed, and the film log shows no error.
Closing a group works in the same film, but it goes through the daemon's `Pack` call.

## What is known

- Detection is sound: in `pkg/group`, `Detect`, then `Remember`, then a move into a group of two sessions on one branch places the session.
- The notice proves nothing: `pkg/render/move.go` prints "moved to <group>" whether the write worked or not.
- The write is `commands.Actor.move`, then `editGroups` on the `GroupStore`, into `groups.json`, which the daemon is meant to notice and group again.
  City and daemon resolve the same path (`appd.GroupsPath`), and neither is given `--home` in the film.
- So the break is between the city writing `groups.json` and the daemon grouping again: either in 0.5.0 itself, or in how the film runs the two (a read-only root and `HOME=/tmp`).

[Item 364](364-moving-a-session-into-a-team-s-group-is-dropped.md) fixes a different cause, moves placed before teams form, which this is not: these groups aren't teams'.

## What it wants

Find which side breaks first.
If 0.5.0 drops moves for everyone with a daemon, this is the worst defect in the release and wants a 0.5.1.
Reproduce it outside the film: a side daemon beside Aria's, as the release's L1–L2 run, with its own socket, config and XDG directories, never her live one.
If it is the film's environment only, fix the film, and make the notice say so when the write fails.
Either way, the notice should only say "moved" once the move has taken, and a test should hold that.
Item 362 drops its move-in and convoy shots until this is fixed, and adds them back from the release that fixes it.

## Answered while building

- **The cause** (item 365's session, 2026-11-07): the city writes a move to `groups.json` in the state directory and tells the daemon nothing.
  The daemon reads that file again only when it rescans. It rescans on fsnotify events in `~/.claude`, or on an explicit call such as `Pack`, and it never watches the state directory.
  So a move takes only at the next write anywhere in `~/.claude`: under a second while a session works, and never on a quiet home or in the film's static one.
  Every `editGroups` write has the same gap: rename, take out, mute, the first-run review, and a new session's `StartedFrom`.
  The code is unchanged since 0.4.1, so this isn't new in 0.5.0.
  Item 364's duplicate ids were ruled out as the cause.
- **The fix and slice 1's test tree** (roadmap manager, 2026-11-07): approved. The loader names the files it reads outside `~/.claude`, so far `groups.json`. The watcher adds that file's directory but rescans only for that file's events, since the daemon writes its own stores beside it. The case where the directory doesn't exist yet is in scope.
  The notice half (say "moved" only once a snapshot shows the move, and say when the write failed) follows as slice 2, with its own tree.
- **No repro with the release binaries** (roadmap manager, 2026-11-07): the code is unchanged since `v0.5.0`, and the `pkg/daemon` test with a real watcher stands in for it.
- **Slice 2's notice tree** (roadmap manager, 2026-11-07): approved. A move first says "moving to X…", then "moved to X" once a snapshot shows the session there.
  A failed write keeps its error notice, and no "moved" covers it.
  If ten seconds pass without the move showing, the notice says "the move to X has not taken", in the error tone.
  A second move replaces the first's wait.
