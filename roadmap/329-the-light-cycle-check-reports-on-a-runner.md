# 329. The light-cycle check gates on a GitHub runner, where every other stress check reports

**Fixed 2026-11-02 (`652b892`, r1228). Filed 2026-11-03 (r1227), from 0.3.5's release dry run. Nobody's call — Aria's rule from items 303, 305 and 306 applies.**

The 0.3.5 release dry run failed in its performance job on `TestLightCycleGivesItsMemoryBack` (+8.0 MiB, llvmpipe), while the stress city's frame bar beside it logged 17.5 ms against 16 and did not gate.
Aria ruled for the stress city (2026-10-27): on CI the stress checks report, and the reference machine gates.
The light-cycle check, landed after that ruling, gates on the runner.

## The fix

On a GitHub runner the light-cycle check reports its numbers and does not fail, through the same switch the stress city uses (items 303, 305, 306); on the reference machine it gates as now.
A test that the switch covers it.

## Closed

Both light-cycle tests now hold each light through `holdCycle`, which goes through `stressGateFor` and `holdToBar`: with CI set they log the two settled readings and the margin, and without it they fail as before.
`TestTheLightCycleGate` (`testing/acceptance/lightcycle_gate_test.go`) covers both sides.
The checks that every measure was logged and the record is unbroken still fail everywhere.
