# 339. The stress city's measures follow the wall clock, so a night run does 3.5% more work than a day run

**Open. Filed 2026-11-03 (r1255), from the performance manager's bisect of a 130.5 → 135.1 M instruction rise that no commit caused. Nobody's call — a defect in the method, after 0.4.0.**

`bigHistory` is dated relative to `time.Now()` and the city follows the clock, so a stress run after nightfall draws the lights: 135.1–135.2 M instructions a fitted tick at night against 130.5 M by day, at the same commits (`~/.local/state/botropolis-perf/instr-bisect-20261103-0310/`).
A gate that runs at a different hour reads a different city.

## The fix

The stress measures pin their light to day (`--set light=day`, item 308's key), with the night reading logged beside, ungated, as the next-fastest cores are (item 330); the instruction count then compares across runs.
A test that the gated reading is by day whatever the clock says.
