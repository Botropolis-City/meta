# 223. The staged metropolis names most of its districts "millrace"

**Fixed 2026-10-24 (`30913bb`, r985). Filed 2026-10-24 (r966), noticed by item 162's session. Nobody's call — a defect.**

**Where it shows.** The `metropolis` demo scenario, staged and shown at fit with labels on (`dist/item-162-options/shore/fit-before.png` in item 162's worktree, or the overview without `h`): nearly every district's label reads "millrace".

**Where to look.** Either the scenario's corpus gives many projects the same name or folder (`botropolis/demo/scenarios/metropolis.yaml` and its staging), or the label is taken from the wrong district, such as a shared variable captured in a loop. Check the staged corpus's project names first: if they differ, it is the label.

## The fix

Each district is labelled with its own project's name. Because the website's clips are filmed from these scenarios, check every scenario's labels while here.

Tests: staging the metropolis gives as many distinct district labels as distinct projects; a fit frame for Aria.

## Answered while building

- **The cause** (the session "item 223", 2026-10-24): the district plates are right; the "millrace" plates are group badges. Staging moves each recording so its newest line sits at `ago`, and the recordings are minutes long, so every working session in a staged city looks started within minutes of the others, and `pkg/group`'s detector, counting starts within a minute as related, chains them into one group named from their words. Every multi-session scenario has it, and it swallows the metropolis's harbor team.
- **The fix** (manager, 2026-10-24): in demo staging only, no detector change: a placement's optional `started:` says how long ago its session opened, staging moves the transcript to begin then and sets `startedAt` to match, keeping the newest line at `ago`; the scenarios get starts that read like a real day. The guard compares each staged scenario's groups with a list the scenario declares (its teams, plus any inferred group it means to show), not with "teams only", so a scenario may still show the detector at work on purpose.
- **The test tree** (manager, 2026-10-24): approved as sent, with that guard reading the scenario's declared groups; then a metropolis overview still for Aria.
- **The landing's two failures** (manager, 2026-10-24): the label checks needed a group badge and station label in workday and workshop, which only the false groups gave; each scenario now stages one deliberate pair of sessions in two districts started together and lists it in `groups:`, under the ruling above. And the metropolis, a changed scene with one group line where it had two, takes 26 draw commands by day and 43 by night against ceilings of 25 and 42 with no code changed; the ceilings rise to the re-measured counts, citing item 223, under the target of 70, and [item 236](236-where-a-vehicle-stands-changes-a-frames-draw-count.md) brings them back down once it finds what makes the count move with the scene.

## Closed

Fixed in demo staging, as answered above, in three botropolis commits: `30913bb` (r985) gives a placement `started:` and a scenario `groups:`, gives every scenario starts that read like a real day, and adds `testing/integration/demo/scenarios_test.go`, which stages every scenario and fails on a group it does not list or one it lists and does not form, both ways;
`3862e73` (r986) gives workday and workshop one deliberate pair each, so the label checks keep a badge and a station to lay out;
and `a32c5cf` (r987) raises the frame's draw-command ceilings to the re-measured 26 and 43.
The guard was red on the old scenarios before the fix, and the stage tests were red before `started:` existed.

**Deviation, flagged for Aria:** the item guessed at the district labels, and they were right all along; the fix is to the staged corpus's start times, not to any label.
The test the item named, distinct district labels per project, would have passed before the fix, so the guard tests the groups instead.

**For Aria to judge:** the metropolis overview before and after, in botropolis's `.claude/worktrees/item-223/dist/item-223/` (`overview-before.png`, `overview-after.png`), to be kept when the worktree is tidied: after, the only badges are the harbor team's.
The top bar's rates fall from about 15 M/h fresh to about 100 k/h, because each session's tokens now spread over hours rather than minutes; spend, PRs and errors are unchanged.
The website's clips change once they are re-filmed for the next release.
