# 253. A team lead's messages to its teammates are never road traffic

**Open, in progress since 2026-10-25 in the session "item 253". Filed 2026-10-25 (r1044), found by item 105's session recording a real agent team. Nobody's call — a defect.**

Depends on: nothing

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
