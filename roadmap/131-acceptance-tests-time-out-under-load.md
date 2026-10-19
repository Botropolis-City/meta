# 131. The acceptance tests run past go test's default timeout under load

**Fixed 2026-10-18 (`ea9542e`, r669). Filed 2026-10-18 (r667), from what item 129 found. Nobody's call — a defect.**

At a load average of about 63, a local `make test` hit `go test`'s default ten-minute timeout in `testing/acceptance`; the same suite took twelve minutes with `-timeout 40m`. `make test-acceptance` passes no `-timeout`, so on a busy machine the suite panics with a stack dump rather than finishing.
CI's Linux job takes about four and a half minutes, so CI has room; the problem is local runs while several item sessions test at once, now the normal case.

## The fix

Give `make test-acceptance` (and `test-acceptance-changed`) an explicit `-timeout` well above the suite's loaded run time, say why in the Makefile, and keep CI's own value; separately, look at whether the slowest tests (item 129's lint probe, the scratch-module probes from item 117) can share one scratch copy so the suite gets shorter rather than only given longer.

Tests: none beyond the suite completing at load; record the suite's time before and after.

## What landed

`ea9542e` (r669): `make test-acceptance` passes `-timeout ${ACCEPTANCE_TIMEOUT}`, 40m by default, and `test-acceptance-changed` carries the same value through `GOFLAGS`, which `go test` applies and `go run` ignores — checked with a 1ms value, which panicked the test and left the tool's help untouched.
CI sets `ACCEPTANCE_TIMEOUT: 10m` on its `make test lint` step, its effective value until now, so a hang there still fails fast.

Before: 219s, at a load average rising from 3 to 15.
After: 262s at about 22, passing.

## Why the scratch copies stay separate

The four scratch-copy tests took 135s of the 219: `TestTargetedRuns` 57s, `TestTheCacheSeesTheBinary` 30s, `TestScriptsAreInTheCacheKey` 29s, `TestLintChecksFormatting` 20s.
A fresh copy costs about 5s more than reusing one (12s against 7s for one `go test` at a load of 20), because a new directory recompiles the module; the suite makes about six, so even free sharing would save about 30s.
The rest is the repeated `go test` runs and rebuilds after each probe, which is what those tests assert on.
And every one of them changes its copy — probes in `pkg/app`, `pkg/render` and `pkg/state`, a git commit, a new file — and two assert on the build cache's state, so a shared copy would make each test's result depend on what ran before it.
Not worth 30s.
