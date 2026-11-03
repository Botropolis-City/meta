# 337. Item 334's socket tests fail on macOS, so CI on main is red

**Fixed 2026-11-03 (`3acddcf`, r1245). Filed 2026-11-03 (r1243), from CI at `01dcc84`. Nobody's call — a defect; CI on main stays green (Aria's rule).**

`TestCityActorSocket` (item 334, `pkg/app`) fails on both macOS runners: under `--home` without `--socket`, packing and recording a close-up return an unexpected error instead of the refusal, while Linux passes.
The test plants a fake listener at the default socket path under a temporary `XDG_RUNTIME_DIR`; on macOS the default socket path is chosen differently, so the test's fake and the code's default disagree, or the Unix socket path exceeds macOS's 104-byte limit under the temp dir.

## The fix

Find which (run the test on a macOS runner with the error printed), and make the test and the code agree on the default socket's path on every platform; the refusal must hold on macOS as on Linux.
CI green on main is the proof.

## Closed

It was the length.
On macOS the default socket is under `HOME`, in `Library/Caches/botropolis/`, and the tests' isolated `HOME` sat under the runner's `/var/folders/…/T/`, so the path came to 118 bytes, over `sun_path`'s 104, and the fake daemon's `bind` failed with `invalid argument`.
The code was right; the staging was not.
Item 336's `TestHomeSubcommandSocket` failed the same way.

`3acddcf` stages `HOME` and `XDG_RUNTIME_DIR` under `/tmp` in all three tests, through `stageDefaultSocket` in `pkg/app/socket_stage_test.go`, and `listenAt` now fails fast with the length when a staged socket would not fit, at the manager's request.
`TestStageDefaultSocket` was red at 118 bytes on Linux under a `TMPDIR` as long as a macOS runner's.
CI run 41600128436 on main passed on both macOS runners.
