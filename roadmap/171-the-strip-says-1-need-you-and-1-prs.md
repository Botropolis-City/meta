# 171. The strip's counts read "1 need you", "1 prs", "1 errors" and "1 subagents"

**Fixed 2026-10-20 (`6c54c60`, r791). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

The strip along the top of the city writes its counts with a fixed form, whatever the number:

| chip | where | with one |
| --- | --- | --- |
| needs you | `CountLabel`, `botropolis/pkg/city/summary.go` | 1 need you |
| pull requests | `StripChips`, `botropolis/pkg/ui/strip.go` | 1 prs |
| errors | `StripChips` | 1 errors |
| subagents | `StripChips` | 1 subagents |

Every demo scenario with one of them shows it: `hamlet` reads *1 need you*, and `layers` reads *1 prs* at about (1000, 16) in a 1920×1080 frame.
The card spells the same thing *PRs*, so the strip also disagrees with the card about the case.
The lens panel under it says *1 session needs you* correctly, because it is built elsewhere.

The fix is a plural helper for these four chips, and *PRs* to match the card.
`strip_test.go` and the `CountLabel` tests can pin each with one and with two.

## Fixed

`format.Count`, in `botropolis/pkg/format`, writes a count with its noun agreeing, and every count this item named uses it.
The strip and the window title read *1 needs you* and *2 need you* through `CountLabel`,
and the strip's other chips read *1 subagent*, *1 PR* and *1 error*.
*PR* is capitalised to match the card.

**The fix is wider than the item asked**, with the manager's approval.
The same *1 need you* was on the sidebar's project row (`botropolis/pkg/ui/sidebar.go`) and the City Plan's badge (`planCounts`, `botropolis/pkg/render/cityplan.go`),
and both use the helper now.
The window title was fixed along with the strip, because `Headline` goes through `CountLabel`.

Tests pin each count with one and with two: `TestCount`, `TestCountLabel`, the headline table, `TestStripChips`, `TestSidebarProjectDetail` and `TestPlanCounts`.
Each went red first, for the stated reason.

**Frame**, approved by Aria on 2026-10-20: `botropolis/docs/screenshots/r787-item-171-strip-counts-before-after.png`, the `layers` and `hamlet` strips from the demo corpus before and after, stacked.
It was drawn at r787 and landed at r792, behind items 174 and 166.
It is cited as a path because the main botropolis checkout had not pulled it when this closed.

Not fixed here: `botropolis bar` prints its counts with the raw state name, *2 needs-you* (`botropolis/pkg/commands/bar.go`).
That went to the manager to file.
