# 256. The test-cache acceptance tests sometimes see no cache hit when the machine is busy

**Open. Filed 2026-10-26 (r1058), seen twice in a day by item sessions landing. Nobody's call — a flaky test.**

Depends on: nothing
Landed: slice 1 (`7ff52f4`, r1088).

Two acceptance tests built by [item 117](117-acceptance-tests-cached-past-code-changes.md) run `go test` twice in a scratch copy of the module and assert the second, unchanged run reports `(cached)`:
`TestScriptsAreInTheCacheKey` (`botropolis/testing/acceptance/subprocess_test.go`) and `TestTheCacheSeesTheBinary` (`botropolis/testing/acceptance/cache_test.go`).
On 2026-10-25 item 95's landing failed in the first ("the second identical run in a scratch copy wasn't (cached)") with a change that only added three images and a changelog line; on 2026-10-26 item 105's slice 7, a YAML-only change, failed in the second the same way. Both passed on a rerun, and neither change can reach what those tests measure.

So the second run sometimes misses Go's test cache for a reason outside the code: a likely suspect is something the cache key reads that differs between two runs a moment apart on a busy machine — an environment variable another parallel test sets, a file's modification time inside the scratch copy, or `GOCACHE` being trimmed or written concurrently by the many builds running beside it.

## The fix

Find what differs between the two runs: run the pair with `GODEBUG=gocachehash=1` (which prints what each test's cache key hashed) under load until it misses, and diff the two keys.
Then make the scratch run's inputs fixed (its own `GOCACHE`, environment and file times), so the test asserts only what item 117 asked: an unchanged module is cached, a change it can see is not.

Tests: the two tests pass at a load like a landing's, many times in a row; and mutated, a change under `pkg/render` still breaks the cache as item 117 requires.

## Answered while building

- **What was found** (item 256's session, 2026-10-26): no miss in about 700 second runs, warm and fresh copies, one process and four, loads 6–50, with `GODEBUG=gocachetest=1` on; the two misses on record were each the first scratch pair in their test process. Ruled out: the recorded inputs, `go clean -testcache`, the daily trim, a toolchain upgrade, a full `/tmp`. Left: the build cache the scratch runs share with every session, and directory mtimes in a fresh copy, which go also hashes.
- **What lands** (manager, 2026-10-26): every scratch `go test` runs with `GODEBUG=gocachetest=1` and `GOFLAGS` cleared, so a miss names its reason, and the scratch copy backdates directories as well as files; not a private build cache, which would add 35–70 s and about 700 MB to every landing for a cause not shown. The item stays open until a miss reports its reason.

## What working it found (2026-10-26)

**It did not reproduce: 0 misses in about 700 second runs**, each with `GODEBUG=gocachetest=1`, so a miss would have printed go's reason.
235 pairs ran in one warm scratch copy on the system Go, and 300 more with make's `GOTOOLCHAIN=go1.27.2 CGO_ENABLED=0`.
20 rounds ran in a fresh copy each, landing-style with `BOTROPOLIS_ACCEPTANCE_BINARY`.
32 rounds ran as four test-binary processes at once, as a landing runs them, about 80 pairs.
Loads ran from 6 to 61 on the 14-core machine.

The two misses on record since item 209 are item 95's (`TestDemoCorpusIsClean`, 2026-10-25 21:43Z) and item 105's (`TestStatus`, 2026-10-26 07:52Z).
Both were the first scratch pair in their test process, in a small landing whose acceptance stage took 64–85 s,
and both second runs really ran (2.2 s and 3.7 s), so neither was a replay.

**Ruled out**, from cmd/go's test cache (identical in go1.27.2 and 1.27.3) and the testlogs the two inner tests record:

- the inputs: the only in-module paths they record are the copied fixtures and demo files, dated an hour back, `tools/` and its script, and the variables `PATH`, `TMPDIR`, `GOTMPDIR` and `PWD`, and nothing writes into the copy between the two runs;
- `go clean -testcache`: `testexpire.txt` dates from June;
- the daily cache trim: it ran at 22:13Z, matching neither miss;
- a toolchain upgrade: pacman shows none near either;
- a full `/tmp`: 32 GB, 1.1 GB used.

**What is left is what the scratch runs share with every other session: the machine's `GOCACHE`.**
A cached test result is stored by content, and its content is only `ok  <package>  2.241s`, so every run of the package that lands on the same millisecond count shares one file; one written at 02:03 by another run was found.
The standard library's and dependencies' build entries are shared too.
Nothing made them interfere on purpose, so this is the surface left, not a cause shown.

**A miss now says why.** Slice 1 runs every scratch `go test` with `GODEBUG=gocachetest=1`, so the failure prints go's reason, such as `input list not found` or a file too new, under the assertion.
It also dates the copy's directories with its files, since go hashes a directory's time and its entries' times.
go's 2 s "too new" refusal applies to regular files only (`hashOpen` in `cmd/go/internal/test`), so the directories' times fix an input but could not have been what refused the cache.
`TestScratchGoTest` and a new leaf of `TestScratchModule` were red before it.
With `binary_test.go`'s `app.Main` reference removed, a change to `app.Run` still replays a cached pass and fails the test, and with it in place the `pkg/render` probe still breaks the cache.

The private build cache's cost, declined above, was measured as one cold build of the acceptance package: 35 s and 358 MB at a load of 19.
