# 315. Opening the six-hundred-district city costs about three CPU-seconds, against a budget of one

**Open, in progress since 2026-10-28 in the session "item 315". Filed 2026-10-28 (r1197), from item 311's CPU bar. Nobody's call — the budget is set (`performance/budgets.md`, `df54c13`); the code is over it.**

The performance manager set the city's own CPU from start to its first frame on the 600-district fixture at no more than 1 CPU-second, `--record` included.
After item 311's fix (`1259a1e`, r1197) a recording city spends 2.7–3.3 CPU-s, and a plain headless city 2.55, so it is the opening's cost, not recording's.
Item 311's profile names two parts:

1. **The collector spirals at the city's 300 MiB `GOMEMLIMIT`:** the live heap is 267–399 MB around the first frame, and about 250 collections run in under a second, about 1.3 CPU-s.
   A live heap above the limit cannot be collected below it, so the limit makes the collector run flat out.
2. **About 1.4 CPU-s in llvmpipe during the opening**, probably the atlas upload.

## The fix

Bring the opening under the budget: a live heap at the first frame that the limit can hold, or a limit the stress city's peak bar allows (1 GiB) without spiralling, which is Aria's call if it changes the 300 MiB she set; and an opening that uploads only what the first frame draws.
Item 311's test, `it should spend at most 1 CPU-second before its first frame`, held unlanded in its worktree, lands with this item, red first.
The budget is the target: if it cannot be met, bring the evidence to Aria; do not loosen it.
