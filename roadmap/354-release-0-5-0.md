# 354. Release 0.5.0

**Open. Filed 2026-11-06 (r1266) at Aria's request. Nobody's call — Aria named what it holds; she confirms the number when the candidate is cut.**

Depends on: 340, 348, 349, 350, 351, 352, 353

The second half of the split recorded on [item 349](349-release-0-4-1.md): Aria, 2026-11-06, *"Do the split, but let's not soak until after 0.5.0"*.

## What it holds

- Item 348, neighbourhoods and the form of a group's line, judged on frames.
- The controls redesign, items 350 to 353, *Controls, parts 1 to 4*, which Aria asked for in the next release through the design agent.
- Item 340, the rescan drift that 0.4.0 and 0.4.1 shipped red; it wants a quiet machine, so it runs once the item sessions thin out.

Aria named 0.5.0 when she chose the split; under the pre-1.0 rule a 0.X is for a breaking change, and whether the controls redesign is one is hers to confirm at the cut, so the number is written here as she said it.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.4.0 did (item 338): one candidate, a landing freeze from it to the tag, the re-film, S1–S10, L1–L2, A1–A7, the dry run, the release, the AUR packages and the site.
**The soak runs after this release** (Aria, 2026-11-06), once, on the released build, and stands for 0.4.1 too, whose soak she waived; its record and verdict go here, and a verdict over budget is a new item against 0.5.1.

## Answered while building

- **Item 340 starts once 0.4.1 is tagged** (Aria, 2026-11-06): it wants a quieter machine than tonight's, and it compares the rescan's profile at r1209 with now, so both are measured under the same load.
