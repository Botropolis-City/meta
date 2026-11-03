# 330. The stress city's fitted frame reads over its bar in the full suite and under it alone, so a neighbour weighs on it

**Fixed 2026-11-03 (`899fcb5`, r1236). Filed 2026-11-03 (r1228), from 0.3.5's release gate. Nobody's call — a defect in the suite's order.**

Landed: slice 1 (`d29223b`, r1233).
Landed: slice 2 (`899fcb5`, r1236).

Twice the full `make test-performance` has read the 600-district city's fitted frame over its 16 ms bar — r1201 16.03, r1228 16.45 — while the subtest alone, run six times quiet at the same commit, read 14.2–14.5 ms every time (performance manager, 2026-11-03).
So something earlier in the suite occasionally leaves the machine, the disk cache or the GPU warm or busy enough to cost a millisecond or two, and a release gate can fail on a neighbour.

## The fix

The stress city's frame tests run first in the suite, or in their own process after a settle, so nothing of the suite's own runs ahead of them; and the suite records what ran before a stress reading, so a spike can be traced.
A test that the order holds.

## Answered while building

- **The cause** (item 330, 2026-11-03): not the suite's order but the core the tick lands on: the same 131 M instructions take 14.9 ms on a P-core, 21.3 on an E-core, 38.6 on an LP-core; every reading over 15.9 ms started busy or queued behind a landing.
- **Pinning** (performance manager, 2026-11-03): the stress measures run on the fastest cores by sysfs max frequency, bars unchanged, since the 16 ms bar was set from runs that landed there; "on a fast core" goes into budgets.md and method.md.
- **An E-core bar?** Aria, 2026-11-03: *"Report it ungated"* — the E-core reading and instructions per frame are logged beside the gated one, no second bar.

## Closed

The neighbour was the machine, not the suite: the stress frames already ran first in their process, and the quiet check ran before `make test-performance` queued for the landing lock, so in r1222 and r1228 a landing ran between the check and the reading.
On this hybrid chip the scheduler moved the ticks between P- and E-cores, and the same work cost half again as much on an E-core.

- **Slice 1** (`d29223b`, r1233): `tools/settle` waits for the method's bars (load under 3 over 1 minute and 4 over 5) once the lock is held, and says how long and at what load; on CI it only says the load.
  Each stress reading logs the load as it began, its median instructions a tick and the cores its ticks ended on (`measure.Tally`).
  `TestPerformanceLocked` holds the settle after the lock.
- **Slice 2** (`899fcb5`, r1236): each reading held to a bar runs on the fastest cores, grouped by sysfs maximum frequency (`measure.CoreClasses`, `measure.Pinned`), and the same measure on the next-fastest is logged beside it, held to no bar.
  Quiet, after settle: fitted 14.59 ms on cores 0–3 and 21.60 on the E-cores, at 130.5 and 131.2 M instructions a tick.
  Unpinned at load 15, the new check failed red, with fitted ticks ending on E-core 11.
- **The order** (`7b60936`, r1240): `TestTheStressCityMeasuresFirst` puts the performance tier in go test's order and fails when another performance test runs ahead of the stress frames; a mutant turned it red.

Bars unchanged.
For the performance manager: `performance/method.md`'s quiet step can point at `make test-performance`'s own wait now, and budgets.md and method.md still need "on a fast core", as answered above.
