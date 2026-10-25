# 105. The demo cannot record or stage an agent team

**Open, in progress since 2026-10-25 in the session "item 105". Filed 2026-10-17 (r561) at Aria's request, from item 89. Nobody's call.**

Depends on: 89 (slice 5)

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
