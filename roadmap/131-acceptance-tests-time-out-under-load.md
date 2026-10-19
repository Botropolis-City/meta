# 131. The acceptance tests run past go test's default timeout under load

**Open. Filed 2026-10-18 (r667), from what item 129 found. Nobody's call — a defect.**

At a load average of about 63, a local `make test` hit `go test`'s default ten-minute timeout in `testing/acceptance`; the same suite took twelve minutes with `-timeout 40m`. `make test-acceptance` passes no `-timeout`, so on a busy machine the suite panics with a stack dump rather than finishing.
CI's Linux job takes about four and a half minutes, so CI has room; the problem is local runs while several item sessions test at once, now the normal case.

## The fix

Give `make test-acceptance` (and `test-acceptance-changed`) an explicit `-timeout` well above the suite's loaded run time, say why in the Makefile, and keep CI's own value; separately, look at whether the slowest tests (item 129's lint probe, the scratch-module probes from item 117) can share one scratch copy so the suite gets shorter rather than only given longer.

Tests: none beyond the suite completing at load; record the suite's time before and after.
