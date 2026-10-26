# 256. The test-cache acceptance tests sometimes see no cache hit when the machine is busy

**Open. Filed 2026-10-26 (r1058), seen twice in a day by item sessions landing. Nobody's call — a flaky test.**

Depends on: nothing

Two acceptance tests built by [item 117](117-acceptance-tests-cached-past-code-changes.md) run `go test` twice in a scratch copy of the module and assert the second, unchanged run reports `(cached)`:
`TestScriptsAreInTheCacheKey` (`botropolis/testing/acceptance/subprocess_test.go`) and `TestTheCacheSeesTheBinary` (`botropolis/testing/acceptance/cache_test.go`).
On 2026-10-25 item 95's landing failed in the first ("the second identical run in a scratch copy wasn't (cached)") with a change that only added three images and a changelog line; on 2026-10-26 item 105's slice 7, a YAML-only change, failed in the second the same way. Both passed on a rerun, and neither change can reach what those tests measure.

So the second run sometimes misses Go's test cache for a reason outside the code: a likely suspect is something the cache key reads that differs between two runs a moment apart on a busy machine — an environment variable another parallel test sets, a file's modification time inside the scratch copy, or `GOCACHE` being trimmed or written concurrently by the many builds running beside it.

## The fix

Find what differs between the two runs: run the pair with `GODEBUG=gocachehash=1` (which prints what each test's cache key hashed) under load until it misses, and diff the two keys.
Then make the scratch run's inputs fixed (its own `GOCACHE`, environment and file times), so the test asserts only what item 117 asked: an unchanged module is cached, a change it can see is not.

Tests: the two tests pass at a load like a landing's, many times in a row; and mutated, a change under `pkg/render` still breaks the cache as item 117 requires.
