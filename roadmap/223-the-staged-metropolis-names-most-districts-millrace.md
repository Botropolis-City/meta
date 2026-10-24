# 223. The staged metropolis names most of its districts "millrace"

**Open, in progress since 2026-10-24 in the session "item 223". Filed 2026-10-24 (r966), noticed by item 162's session. Nobody's call — a defect.**

**Where it shows.** The `metropolis` demo scenario, staged and shown at fit with labels on (`dist/item-162-options/shore/fit-before.png` in item 162's worktree, or the overview without `h`): nearly every district's label reads "millrace".

**Where to look.** Either the scenario's corpus gives many projects the same name or folder (`botropolis/demo/scenarios/metropolis.yaml` and its staging), or the label is taken from the wrong district, such as a shared variable captured in a loop. Check the staged corpus's project names first: if they differ, it is the label.

## The fix

Each district is labelled with its own project's name. Because the website's clips are filmed from these scenarios, check every scenario's labels while here.

Tests: staging the metropolis gives as many distinct district labels as distinct projects; a fit frame for Aria.
