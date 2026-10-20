# 180. Three lens panels say things that read as wrong beside the strip

**Open, in progress since 2026-10-20 in the session "item 180". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154, from its matters of taste, at Aria's request. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`e4bea15`, r827).

Each lens's panel, top left, carries a count and a hint, built in `botropolis/pkg/city/lens.go`.
Three of them read as wrong next to the strip above them, though each is right on its own terms.

![Attention, Work and Cost beside the strip](../docs/references/180-the-lens-panels-wording-disagrees-with-the-strip.png)

Shots: `buildings` at fit; `layers` with `Digit2` and with `Digit3`; 1920×1080, crops of the top-left corner.

- **Attention, with nobody waiting**, says *"0 sessions need you"* and then *"Press tab to go to the next session that needs you."*
  The hint is fixed: `hint` returns it for Attention whatever the count. With none waiting it points at something that is not there; it could say so, or say what tab will do.
- **Work** says *"1 group, 0 your move"* while the strip says *2 need you*.
  The panel counts groups whose move is yours (`s.snapshot.Groups`, `MoveYours`); the strip counts sessions. Two sessions waiting outside any group make it read as a contradiction.
- **Cost** says *"$1.32 across 11 sessions"* while the strip says *$1.25 24h*.
  The panel sums what each card says its session spent (`spend()`, the high end of a priced range), over each session's whole life; the strip is the last 24 hours. Neither says which window it is beside the other.

The fix is wording: Attention's hint follows its count, Work says what it counts ("0 groups waiting on you"), and Cost names its window ("$1.32 over these sessions' lives") and whether it is a range.
The lens tests already pin each count's text, so each change is a test changed first.
