# 69. The 10% CPU bar is missed, and no item owned that fact

**Closed 2026-10-23 by adjudication: answered by Aria on 2026-10-19 (performance/budgets.md); meeting the bar is item 161's. Filed 2026-09-29 out of adjudicating the eight unresolved entries in [audit-r96.md](audit-r96.md). Aria's call, because the question is whether 10% is still the bar.**

Five entries measured this and every one of them is now closed: bug 22 set the bar and met half of it, bug 28 recorded 14.5%, bug 29 found the lever, bug 31 measured 14.2% after phase 19 took 20% off, and item 60 re-measured 14.4% at r268 and found it unmoved.
**Not one of them was the item that owned the gap**, so closing them all would have retired the number without anyone ruling on it.
That is the whole reason the adjudication was worth doing.

**Where it actually stands, measured on Aria's desk at r268** (`DISPLAY=:0`, i3, floating 900x700, two sessions working):

| condition | cost |
| --- | --- |
| busy, 30 fps | **15.3%** of a core |
| like-for-like against phase 19 | 14.4%, unmoved inside the spread |
| quiet, gate at 12 fps | 6.8% |
| `reduced_motion` | 8.1% |
| scenery dropped | 13.2% |
| unfocused or hidden | 0.3–0.4%, zero frames |

So the bar is **met three ways when the city is quiet and missed by half again when it is busy**, and the unfocused case beats its own 1% bar by a factor of three.

**Three honest readings, and the choice is Aria's rather than mine:**

1. **The bar was set for the wrong condition.** It was written in bug 22 against *idle and visible*, and idle-and-visible now costs 6.8%. A busy city at 15.3% is not what it was measuring, and 10% may simply be the wrong number to hold a busy city to.
2. **The bar stands and the work is not done.** Phase 19 found 20% by hiding networks; nothing since has looked for the next 35%, and item 60's quiet row has an admitted flaw — its fixture daemon reports no sessions, so that city has no buildings and 6.8% is not what a real quiet city costs.
3. **Retire it.** It has been missed continuously since phase 18 and the city is in daily use anyway, which is evidence about how much it matters.

**What it would take to answer (2) properly, if she picks it:** a quiet measurement against a real daemon rather than the fixture, because the cheapest row in the table is the one least entitled to be quoted.

## Closed

Answered by Aria on 2026-10-19: `performance/budgets.md` holds a visible, drawing city to ≤ 10% of a core and ≤ 10 ms of CPU a frame, and [item 161](161-drawing-a-frame-costs-41-ms-of-cpu.md) records that it answers this item. The real-daemon measurement this item asked for was taken (r905 and r921, a scratch daemon on a copy of the real state): a focused city on the real history used 61% of a core at fit.
So the bar stands and is still missed; meeting it is item 161's job. Checked by a research agent for the roadmap manager, 2026-10-23.
