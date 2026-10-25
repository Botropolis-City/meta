# 105. The demo cannot record or stage an agent team

**Open, in progress since 2026-10-25 in the session "item 105". Filed 2026-10-17 (r561) at Aria's request, from item 89. Nobody's call.**

Depends on: 89 (slice 5)
Landed: slice 1 (`8deb342`, r1026).
Landed: slice 2 (`a59ad37`, r1027).
Landed: slice 3 (`4e6c9c6`, r1031).

The demo corpus has no agent-team sessions, so nothing that only teams produce can be filmed: a message between teammates is road traffic only through the team's config (`Roads` in `botropolis/pkg/state/state.go` resolves a recipient through `team.Member` to the member's directory, for transcripts carrying a `teamName`), and Claude Code's agent teams are not recorded or staged by the demo tools.
Item 89 found this when it could not film its message vans; Aria chose, on 2026-10-17, to build team support rather than leave vans unfilmed.

## What is missing

- **Describing a team**: `botropolis/demo/scripts/*.yaml` describe one session at a time; a script needs to say "a lead here and a teammate in that project, and this message between them".
- **Recording one**: `botropolis-demo record` (`recordCommand` in `botropolis/cmd/botropolis-demo/main.go`) has to run a team through the CLI it already drives. Agent teams are an experimental Claude Code feature, so the first step is to check that the recorder's invocation can start one at all, and say so in this item before building on it.
- **Staging one**: `demo.Stage` (`botropolis/pkg/demo/stage.go`) writes transcripts into a demo home but no team config, which `claude.ReadTeams` reads from the home's `teams/` directory.
- **Checking it**: the corpus checks (`make demo-check`) must cover the new files, since everything under `demo/` is published in effect.

## Done when

A recorded team session is in the corpus, staged with its team config, and `Roads` shows its message as road traffic in a staged home; then vans and a train along a group line are filmed for Aria from it.
Recording spends tokens: keep it to one short exchange, read the token by reference as item 89 did, and say the cost here.

## Answered while building

- **Spending tokens to record** (Aria, 2026-10-25, asked by the manager): start it, and prompt her when needed. Build the describing, staging and checks first; the token comes through `secret-run` only when the recording runs, and the cost goes in this item.

## Whether the recorder can start a team

**It cannot, as it stands** (2026-10-25).
Claude Code's agent-teams page says that with `-p`, "Claude doesn't spawn teammates, and a subagent that Claude names runs as an ordinary subagent even with agent teams enabled", and `botropolis-demo record` runs every prompt with `-p`.
So recording a team needs a second way to drive the CLI: an interactive session the recorder starts and ends itself.

What a team leaves on disk, read from this machine's own teams by their structure alone:

- each teammate is a session of its own, with its own transcript in its project's folder, not a subagent file under the lead;
- its lines carry `teamName`, which is `session-` and the lead's first eight characters, and its `agentName`;
- it reports to its lead with `SendMessage` to `team-lead`, which `Roads` already resolves;
- `teams/<team>/config.json` names each member with its `cwd`, and Claude Code removes it when the lead's session ends, so a recording cannot rely on exporting it.
- **Recording a team** (manager, 2026-10-25): `-p` never spawns teammates, so a `team: true` script session is recorded interactively, `claude` in a detached tmux session in the recorder's container, the recorder stopping it at the lead's quiet end, its budget or 10 minutes, and stopping it too when the recorder itself is interrupted. Slices 1–3's trees are approved; the corpus check needs every teammate's lead in the corpus.
- **A first-run dialog in the recorder** (manager, 2026-10-25): the recorder's own scratch home, inside its container, is set up with onboarding done, the folder trusted and the bypass-permissions warning skipped, so interactive `claude` opens on its prompt; a test holds that nothing is written outside that home, since trusting a directory in Aria's own Claude configuration is hers alone.

## How a team is recorded

A script session marked `team: true` runs its one prompt in an interactive `claude` under tmux, inside the recorder container, with agent teams on.
The recorder holds it to `budget_usd` itself, by pricing every transcript in the team as it grows, since `--max-budget-usd` is a `-p` flag; it also stops at ten minutes and when it is interrupted.

**First-run dialogs are answered only in the recorder's scratch home** (manager, 2026-10-25): onboarding, folder trust for the toy projects and the bypass-permissions warning are settled in `/home/demo` inside the container and nowhere else.
Doing the same in Aria's own `~/.claude` or `~/.claude.json` is her decision, never the tool's, and nothing is copied from her Claude data.
The workspace test holds a sentinel `~/.claude.json` in a temporary `HOME` unchanged.
- **The demo token** (Aria, 2026-10-25): stored in 1Password as `op:Botropolis/Botropolis Demo Recorder Token/credential` (a token from `claude setup-token`, entered through `secret-run`'s prompt and never on a command line); recordings read it by that reference, which the Makefile's `demo-record` comment names.
- **What the first recording found** (manager, 2026-10-25): it worked in a minute, but Claude Code 2.1.310 writes new line types (`api-request`, `api-request-blob`, `api-request-shape`) holding its system prompt and API settings, a teammate run in-process was not exported, so its spend escaped the cap, and the lead's lines carry no team name. The recording was not committed. Slice 4 makes the scrub an allowlist of the line types the app reads, with `make demo-check` refusing any other type in the corpus, exports and prices every transcript the run wrote, and re-records; the lead's missing team name is decided from the teammate's real shape.
- **The corpus under the allowlist** (manager, 2026-10-25): all 30 corpus transcripts carry line and attachment types the app never reads, among them pieces of Claude Code's own skill and tool lists, published since the corpus began; none is personal or a secret, so history is left as it is. Slice 4 re-scrubs the corpus, reviewed as whole-line removals only, and re-lists its digests; the scenario tests prove staging unchanged, and the full re-film this causes waits for the next release, as filming always does.
