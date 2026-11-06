# 358. The performance gate records nothing of the machine's power state

**Open. Filed 2026-11-06 (r1276), from 0.4.1's release gate. Nobody's call — a gap in the method.**

On 2026-11-06 the fitted frame in `TestACityOfSixHundredDistrictsFrames` read 24.9 ms of CPU a frame at the 0.4.1 candidate overnight, 18.4 ms on a settled rerun, and 38.8 ms the next morning, against a bar of 16 ms.
v0.4.0's own build read 21.9 ms and then 38.6 ms on the same machine, and both builds did the same work, 127.8–127.9 M instructions a tick ([item 349](349-release-0-4-1.md)).
The same work cost twice as much from one run to the next, and the gate could not say why.

## What the machine read

That morning: platform profile `balanced`; RAPL `PL1` and `PL2` both 57 W, the short-term limit no higher than the long-term one; cores reaching about 2.7 GHz of 5.4 under load; package at 49–53 °C; no power daemon running; and thermal throttle counters in the tens of thousands after nine hours up, so it had throttled hard earlier.
None of it is recorded by `make test-performance`, and [the method](../performance/method.md) neither sets it nor checks it, so a run on a clamped machine reads as a regression and a run on a fast one could hide one.

## The fix

The gate records the platform profile, both RAPL limits, the governor and EPP, turbo, AC power and the throttle counters before and after, beside every run's numbers.
It refuses to call a run a measurement when the state is not the one the budgets were set under, the way `settle` already refuses a busy machine — exit 2, "not a measurement", rather than a red.
Which state that is, and whether the budgets were set under it, is for the performance manager to establish from its reports; the method then names it.
