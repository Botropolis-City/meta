# 253. A team lead's messages to its teammates are never road traffic

**Fixed 2026-10-25 (`55e5118`, r1051). Filed 2026-10-25 (r1044), found by item 105's session recording a real agent team. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`a0ec129`, r1052).

Item 105 recorded a real agent team on Claude Code 2.1.310 (one lead, one teammate, $0.01) and read the transcripts' structure:
- the teammate is a session of its own, filed beside the lead, carrying `agentName` and `teamName: session-<8 hex>`, and it messages `team-lead`;
- **the team's name is not the lead's session id**: the lead was `3cab0685`, its team `session-2aa29be8`, and nothing has the id `2aa29be8`;
- **the lead's own lines carry no `teamName`**; what ties it to its team is the result of the `Agent` tool call that spawned the teammate, `toolUseResult.team_name` (and `teammate_id`, `reader@session-2aa29be8`).

So in a real user's city:
- `Roads` (`botropolis/pkg/state/state.go`) skips a session with no team, so a lead's messages to its teammates never travel the road between their districts;
- `leadByTeamName` assumes the team is named after the lead's id, so a teammate's message to `team-lead` resolves only while Claude Code's team config (`teams/<team>/config.json`) still exists, and it deletes that when the lead ends.

## The fix

`pkg/claude` reads the team a transcript leads from its `Agent` results' `team_name`, as `Transcript.LeadsTeam`; `pkg/state` takes a session's team from it when no line names one, and finds a team's lead by it rather than by the name's prefix.

Tests: reading a transcript whose `Agent` result names a team gives the team it leads; a lead whose lines name no team but which leads one is in that team; its message to a teammate is road traffic to the teammate's district; a teammate's message to `team-lead` resolves with no team config present. Fixtures shaped like item 105's recording (structure only). A changelog line, since a user's city changes.

Item 105's demo staging and corpus check, which assumed the same naming, change on top of this.

## Answered while building

- **The tree, and the old naming** (manager, 2026-10-25): approved: `Transcript.LeadsTeam` from an `Agent` result's `toolUseResult.team_name`, `Session.Leads`, a session's team taken from it when no line names one, and `team-lead` found by `Leads`. The prefix match (`session-<lead id[:8]>`) stays as a fallback after it, because users' histories hold transcripts from older Claude Code versions named that way; each path has its own test, and the `Leads` lookup wins when both match.

## Closed

Fixed in `55e5118` (r1051), with `a0ec129` (r1052), as the item asked.
`pkg/claude` reads `toolUseResult.team_name` on a lead's `Agent` results as `Transcript.LeadsTeam`; `pkg/state` gives the session that team and a `Leads` field, so a teammate is no longer cleared as a team of one.
`Roads` finds `team-lead` as the session that leads the team, and a teammate by its agent name among the sessions, when the team config is gone.
Tests: `TestLeadsTeam` in `pkg/claude`, and the new cases in `TestRoads` and `TestSoloTeams` in `pkg/state`, with fixtures shaped like item 105's recording.
**Kept as a fallback** (manager, 2026-10-25): the match on a team named after its lead's id stays, after the `Leads` lookup, because users' histories hold transcripts from older Claude Code versions named that way.
Each path has its own test, and removing the fallback was checked to go red.
**Beyond the item**: `make land`'s gate found the veil had no entry for the new `Session.Leads`, so `a0ec129` veils it as a team name.
The changelog's Fixed section says it: "An agent team's messages travel the road between its districts."
