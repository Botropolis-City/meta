# 305. The stress city's bars cannot gate on a shared runner, so they report there and gate on the reference machine

**Fixed 2026-10-27 (`f675820`, r1184). Filed 2026-10-27 (r1183), from 0.3.3's second release dry run. Nobody's call — Aria ruled.**

After item 303 gave the first map a CI limit, 0.3.3's next dry run (40534785836) failed the 600-district city's fitted frame on the release runner: 22.1 ms of CPU against 16, where the run an hour earlier on the same code read 15.4 ms; the first map passed its 9 s CI limit at 5.2 s.
Shared GitHub runners vary that much between runs, so a bar set for Aria's machine cannot gate there.

Aria, 2026-10-27: on GitHub's runners the stress city's bars are **logged, not gated**; the gate is the performance manager's quiet `make test-performance` on the reference machine, which every release already runs, and every other performance test still gates on CI.

## The fix

`TestACityOfSixHundredDistricts` and `TestACityOfSixHundredDistrictsFrames` log every measure with its bar everywhere, and assert only where `CI` is unset; with `CI` set they say in the log that they report and do not gate, and why. Item 303's 9 s first-map limit becomes part of that report.
Tests: with `CI` unset the bars assert (a measure over its bar fails); with `CI` set the same measure is logged and passes; the log names the mode.
`RELEASING.md` says the reference machine's quiet run is the stress city's gate.

## Closed

`stressGateFor` and `holdToBar` in `testing/acceptance/bigcity_test.go` (`f675820`, r1184) send every bar of `TestACityOfSixHundredDistricts` and `TestACityOfSixHundredDistrictsFrames` through one gate: without `CI` a measure over its bar fails as before, and with `CI` set it is logged as *over its bar, reported and not gated* and passes.
Each test logs its mode first, as *the stress city reports and does not gate: CI is set, and a shared runner's CPU varies too much between runs to hold a bar (item 305); the reference machine's quiet make test-performance gates*.
Item 303's 9 s first-map limit goes through the same gate, so on CI it is reported.
`it should report its frames, or nothing was measured` still asserts everywhere, because it is not a bar.
`TestTheStressCityGate` covers both modes with a fake `t`: the gate and its mode, a measure over its bar failing only without `CI` and logged with it, and a measure within its bar not failing; it was red against a stub first.
Locally with `CI=true` both stress tests passed in report mode (fitted 15.2 ms, first frame 3.8 s).
`RELEASING.md`'s step 4 names the reference machine's quiet `make test-performance` as the stress city's gate, and the release workflow's comment on its performance job says the stress city only reports there.
CI run 40539886848 on `f675820` was green.
The report mode is proven on the release runner only when 0.3.3's next dry run runs the performance job.
