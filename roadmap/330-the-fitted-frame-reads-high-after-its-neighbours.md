# 330. The stress city's fitted frame reads over its bar in the full suite and under it alone, so a neighbour weighs on it

**Open, in progress since 2026-11-03 in the session "item 330". Filed 2026-11-03 (r1228), from 0.3.5's release gate. Nobody's call — a defect in the suite's order.**

Landed: slice 1 (`d29223b`, r1233).

Twice the full `make test-performance` has read the 600-district city's fitted frame over its 16 ms bar — r1201 16.03, r1228 16.45 — while the subtest alone, run six times quiet at the same commit, read 14.2–14.5 ms every time (performance manager, 2026-11-03).
So something earlier in the suite occasionally leaves the machine, the disk cache or the GPU warm or busy enough to cost a millisecond or two, and a release gate can fail on a neighbour.

## The fix

The stress city's frame tests run first in the suite, or in their own process after a settle, so nothing of the suite's own runs ahead of them; and the suite records what ran before a stress reading, so a spike can be traced.
A test that the order holds.

## Answered while building

- **The cause** (item 330, 2026-11-03): not the suite's order but the core the tick lands on: the same 131 M instructions take 14.9 ms on a P-core, 21.3 on an E-core, 38.6 on an LP-core; every reading over 15.9 ms started busy or queued behind a landing.
- **Pinning** (performance manager, 2026-11-03): the stress measures run on the fastest cores by sysfs max frequency, bars unchanged, since the 16 ms bar was set from runs that landed there; "on a fast core" goes into budgets.md and method.md.
- **An E-core bar?** Aria, 2026-11-03: *"Report it ungated"* — the E-core reading and instructions per frame are logged beside the gated one, no second bar.
