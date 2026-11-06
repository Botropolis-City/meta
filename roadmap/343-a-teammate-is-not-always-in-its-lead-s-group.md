# 343. A teammate is not always in its lead's group, and does not move with it

**Open, in progress since 2026-11-06 in the session "item 343". Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — she has said what it should do.**

Depends on: nothing
Landed: slice 1 (`bcd1cec`, r1262).

Aria, on seeing a lead session and one of its teammates in different groups: *"subsessions should always show up in the same group and should move with their parent."*

"Subsession" here means a **teammate**: a member of an agent team, a full session with its own building, tied to its lead by the camp's dashed line ([`camps.go`](../botropolis/pkg/city/camps.go)).
A subagent has no building and no group, so this item does not touch it.

## What happened

A lead with 15 teammates was on the map, none of the 16 in any group.
Aria moved the lead into a new group from its card, and moved the teammate that was asking for her into another.
Every other teammate stayed in no group.
The resting teammates could not be moved at all, since *move to group* is not offered on a resting session ([`scene.go`](../botropolis/pkg/city/scene.go), `ActionMoveToGroup`).
They were put in the lead's group by writing `moves` into `groups.json` by hand, which is the only way there is.

## Why

A team is only evidence that two sessions are related, and three things can override it:

- `related` in `pkg/group/cluster.go` ignores a team that `isCommon` calls too common, one with more than `MaxMembers` members.
- A pair in `notRelated` keeps them apart.
  On the machine above, the lead was in 15 such pairs, one per teammate, and the stored group listing all 16 carried none of them.
- `placeMoved` moves one session.
  A move records that session alone, and `d.moved` then takes it out of detection, so its team stays behind.

## What it wants

- **A teammate is in its lead's group, always.**
  Membership follows from the team after detection and after moves, and neither `isCommon` nor `notRelated` can separate them.
- **A team with no group is in no group together.** The same rule, with nothing to follow: a lead in no group leaves its teammates in none.
- **A move acts on the team.**
  Moving the lead moves every teammate, resting ones included.
  Moving or taking out a teammate from its own card does the same, and the card says it moves the whole team, because moving it alone would break the first rule.
- **Closing a group still packs every member**, which now includes the whole team.

Which session leads comes from what `placeCamps` already uses: the roster's `LeadSessionID`, then the team's session with no `Agent`.
`pkg/group` knows only `Member.Team` today, so it needs the lead too.
A team whose lead is packed or gone is the case to decide while building it: a teammate should still follow the group the lead is recorded in.
Sessions already carrying a move of their own, as those 15 do, must keep working.

Packing a lead does not pack its teammates, and this item does not change that; Aria asked about groups.

## Tests

`pkg/group/detect_test.go` has "it is a teammate in the same agent team", which pins a team as evidence and should become a guarantee.
New cases, in `detect_test.go` and `pkg/commands/move_test.go`: a team above `MaxMembers`, a lead and teammate in `notRelated`, a moved lead with resting teammates, a moved teammate, a teammate taken out, and a team whose lead is packed.

## Answered while building

- **The test tree and design** (roadmap manager, 2026-11-06): approved — `Member.Lead` resolved in `pkg/state` as `placeCamps` does; a teammate sits out detection and a `followLeads` pass puts it in its lead's group at tier Sure with a `SignalTeam`; a team's move is the latest recorded on any of its sessions and is applied to the lead, so the hand-written teammate moves keep working; a not-related pair inside a team is ignored and one between a teammate and an outsider counts for the lead, since a teammate's take-out acts on the team; `Scene.ForTeam` lifts a move, take-out or join on a teammate to the lead so the picker, drag and dive all go through it.
- **A lead recorded nowhere** (roadmap manager, 2026-11-06, from the item's own rules): when the lead is not among the members and no move or stored group names it, its teammates are in **no group, together** — not grouped by detection as today, which could split the team — and a hand move on any of them moves the whole team.
  The worker had proposed letting them group as today; the item's second rule settles it the other way.
- **A resting teammate's card offers move and take out** (roadmap manager, 2026-11-06): the move acts on the team, and the item's report is that the resting ones could not be moved.
- **A team is still a group of its own** (item 343's session, slice 1, 2026-11-06): a team whose lead is in no stored group and was not moved to none forms a detected group of its own, as a team always has; so taking a lead out of a group leaves its team in a group of their own, not in none, and "in no group together" is what a move to none gives.
