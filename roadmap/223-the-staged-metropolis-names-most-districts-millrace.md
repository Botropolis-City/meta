# 223. The staged metropolis names most of its districts "millrace"

**Open, in progress since 2026-10-24 in the session "item 223". Filed 2026-10-24 (r966), noticed by item 162's session. Nobody's call — a defect.**

**Where it shows.** The `metropolis` demo scenario, staged and shown at fit with labels on (`dist/item-162-options/shore/fit-before.png` in item 162's worktree, or the overview without `h`): nearly every district's label reads "millrace".

**Where to look.** Either the scenario's corpus gives many projects the same name or folder (`botropolis/demo/scenarios/metropolis.yaml` and its staging), or the label is taken from the wrong district, such as a shared variable captured in a loop. Check the staged corpus's project names first: if they differ, it is the label.

## The fix

Each district is labelled with its own project's name. Because the website's clips are filmed from these scenarios, check every scenario's labels while here.

Tests: staging the metropolis gives as many distinct district labels as distinct projects; a fit frame for Aria.

## Answered while building

- **The cause** (the session "item 223", 2026-10-24): the district plates are right; the "millrace" plates are group badges. Staging moves each recording so its newest line sits at `ago`, and the recordings are minutes long, so every working session in a staged city looks started within minutes of the others, and `pkg/group`'s detector, counting starts within a minute as related, chains them into one group named from their words. Every multi-session scenario has it, and it swallows the metropolis's harbor team.
- **The fix** (manager, 2026-10-24): in demo staging only, no detector change: a placement's optional `started:` says how long ago its session opened, staging moves the transcript to begin then and sets `startedAt` to match, keeping the newest line at `ago`; the scenarios get starts that read like a real day. The guard compares each staged scenario's groups with a list the scenario declares (its teams, plus any inferred group it means to show), not with "teams only", so a scenario may still show the detector at work on purpose.
- **The test tree** (manager, 2026-10-24): approved as sent, with that guard reading the scenario's declared groups; then a metropolis overview still for Aria.
