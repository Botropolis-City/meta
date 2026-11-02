# 330. The stress city's fitted frame reads over its bar in the full suite and under it alone, so a neighbour weighs on it

**Open, in progress since 2026-11-03 in the session "item 330". Filed 2026-11-03 (r1228), from 0.3.5's release gate. Nobody's call — a defect in the suite's order.**

Twice the full `make test-performance` has read the 600-district city's fitted frame over its 16 ms bar — r1201 16.03, r1228 16.45 — while the subtest alone, run six times quiet at the same commit, read 14.2–14.5 ms every time (performance manager, 2026-11-03).
So something earlier in the suite occasionally leaves the machine, the disk cache or the GPU warm or busy enough to cost a millisecond or two, and a release gate can fail on a neighbour.

## The fix

The stress city's frame tests run first in the suite, or in their own process after a settle, so nothing of the suite's own runs ahead of them; and the suite records what ran before a stress reading, so a spike can be traced.
A test that the order holds.
