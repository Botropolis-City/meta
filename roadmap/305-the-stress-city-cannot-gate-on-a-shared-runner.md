# 305. The stress city's bars cannot gate on a shared runner, so they report there and gate on the reference machine

**Open, in progress since 2026-10-27 in the session "item 305". Filed 2026-10-27 (r1183), from 0.3.3's second release dry run. Nobody's call — Aria ruled.**

After item 303 gave the first map a CI limit, 0.3.3's next dry run (40534785836) failed the 600-district city's fitted frame on the release runner: 22.1 ms of CPU against 16, where the run an hour earlier on the same code read 15.4 ms; the first map passed its 9 s CI limit at 5.2 s.
Shared GitHub runners vary that much between runs, so a bar set for Aria's machine cannot gate there.

Aria, 2026-10-27: on GitHub's runners the stress city's bars are **logged, not gated**; the gate is the performance manager's quiet `make test-performance` on the reference machine, which every release already runs, and every other performance test still gates on CI.

## The fix

`TestACityOfSixHundredDistricts` and `TestACityOfSixHundredDistrictsFrames` log every measure with its bar everywhere, and assert only where `CI` is unset; with `CI` set they say in the log that they report and do not gate, and why. Item 303's 9 s first-map limit becomes part of that report.
Tests: with `CI` unset the bars assert (a measure over its bar fails); with `CI` set the same measure is logged and passes; the log names the mode.
`RELEASING.md` says the reference machine's quiet run is the stress city's gate.
