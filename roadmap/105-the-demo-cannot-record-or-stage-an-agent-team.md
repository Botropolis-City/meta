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
- **The 25 GiB test** (manager, 2026-10-25): `TestStagedMetropolisReadsAsAHeavyUser`, on the re-scrubbed corpus, took the machine's memory (it ran out in 6 s under a 3 GiB cap; 30 MB on the original). Item 240's `openAt` took a recording's opening to be its leading lines at its earliest moment; in 14 transcripts the first prompt is stamped 1–2 ms after a line that follows it, and a dropped `queue-operation` had hidden that, so the opening came back empty and `fillHours` filled from year 1. Fixed inside slice 4: the opening is the leading lines within a second of the earliest, and a fill from an empty or day-early opening refuses, loudly.

## The first recording (2026-10-25)

The first team run worked: the lead spawned `reader` in-process, the reader sent its summary and the lead thanked it, in 1m00s, for $0.0048 as the recorder priced it.
That figure is the lead alone, because the recorder found no teammate transcript to price, and the recording was not committed, since it showed four things:

- **The scrub was a denylist, and Claude Code 2.1.310 writes new shapes past it**: `api-request-shape` (42–50 KB, its system prompt and tool list), `api-request-blob` (message bodies, system-role ones among them) and `api-request` (internal API settings).
  The scrub is now an allowlist (manager, 2026-10-25): it keeps the line types the app reads, and an attachment only for its `model`, and `make demo-check` refuses any corpus line outside the same list.
- **An in-process teammate is not filed or named as a tmux one is**, so a team run now prices and exports every file it wrote under the home's projects.
- **The budget therefore priced the lead alone**, which that change also fixes.
- **The lead's own lines carry no `teamName`** in this version, so `Roads` cannot count the lead's messages to its teammate; what that means for the city waits on the teammate's shape from the next recording.

**The corpus was re-scrubbed to the allowlist**, which failed all 30 transcripts: by type, `atis-latch` 91, `queue-operation` 72, `mode` 5; by attachment, `budget_usd` 158, `total_tokens_reminder` 153, 30 each of `environment`, `deferred_tools_delta`, `agent_listing_delta`, `skill_listing`, `session_context`, `date` and `remote_session_change`, `deferred_tools_record` 8, `silent_turn_reminder` 3, `auto_mode`, `edited_text_file` and `command_permissions` 2 each, and `queued_command` 1.
The review held it to removals: 707 lines dropped and 703 kept byte-identical, with no violation.
**History stays as it is** (manager, 2026-10-25): what was published was Claude Code's own tool and skill listings, with no secrets and nothing personal, and rewriting public history is not worth it.
The re-scrub changes the film cache's key, so the next release's film is a full one, which it would be anyway; nothing was re-filmed for it.

**The re-scrub exposed a fault in item 240's staging.**
`openAt` took a recording's opening to be its leading lines at the earliest moment; in 14 transcripts the first prompt is stamped 1–2 ms after a line that follows it, which a `queue-operation` stamped earlier had hidden.
The opening came back empty, `fillHours` filled from the zero time, 204,963,823 turns at a 45 s pace, and `TestStagedMetropolisReadsAsAHeavyUser` ran out of a 3 GiB cap in 6 s, against 30 MB on the original corpus; uncapped it reached 25 GiB and the machine's low-memory reaper stopped other jobs.
The opening now allows 50 ms of skew, and `fillHours` refuses an empty opening or one more than a day before its recording; the demo integration tests then took 4 s at a 25.5 MB peak.
