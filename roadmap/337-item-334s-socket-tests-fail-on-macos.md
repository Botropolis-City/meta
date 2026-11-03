# 337. Item 334's socket tests fail on macOS, so CI on main is red

**Open, in progress since 2026-11-03 in the session "item 337". Filed 2026-11-03 (r1243), from CI at `01dcc84`. Nobody's call — a defect; CI on main stays green (Aria's rule).**

`TestCityActorSocket` (item 334, `pkg/app`) fails on both macOS runners: under `--home` without `--socket`, packing and recording a close-up return an unexpected error instead of the refusal, while Linux passes.
The test plants a fake listener at the default socket path under a temporary `XDG_RUNTIME_DIR`; on macOS the default socket path is chosen differently, so the test's fake and the code's default disagree, or the Unix socket path exceeds macOS's 104-byte limit under the temp dir.

## The fix

Find which (run the test on a macOS runner with the error printed), and make the test and the code agree on the default socket's path on every platform; the refusal must hold on macOS as on Linux.
CI green on main is the proof.
