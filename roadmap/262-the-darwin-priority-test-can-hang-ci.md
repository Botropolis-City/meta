# 262. The macOS priority test can hang a CI job until it dies

**Open. Filed 2026-10-26 (r1085), seen by item 213's session in CI. Nobody's call — a flaky test.**

Depends on: nothing

CI run 40318079851 (item 213's slice 1) went red on `test-macos (macos-26-intel)`: the step "Background priority against item 138's inversion" (`go test -run '^TestStateChangeDuringBackfillOnDarwin$' ./pkg/daemon/`, with `BOTROPOLIS_DARWIN_PRIORITY_MATRIX=shipped`, from [item 200](200-first-launch-runs-at-full-priority-on-macos.md)) printed nothing until the job was killed, after the unit tests had passed.
The runs of slices 2 and 3, which contain slice 1, passed the same job in about seven minutes, so it is not that change; item 200 found that some background-priority settings can freeze a daemon on macOS, and a test whose daemon freezes can wait past its own timeout without a word.
A step that hangs until the job dies turns `main` red with no message saying why, which Aria's rule — CI stays green — cannot afford.

## The fix

Make the test fail loudly and fast when the daemon stops making progress, rather than wait out the job: a per-phase deadline on progress (not on wall time for the whole test) that names the phase and dumps the daemon's goroutines, and a step-level `timeout-minutes` well inside the job's, so a hang reads as a named failure.
Then find why it hung, from that output: the shipped priority on the Intel runner, or the runner itself.

Tests: the test, with its daemon held frozen by a test-only switch, fails within its phase deadline naming the phase; CI's step has a timeout shorter than the job's.
