# 171. The strip's counts read "1 need you", "1 prs", "1 errors" and "1 subagents"

**Open. Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

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
