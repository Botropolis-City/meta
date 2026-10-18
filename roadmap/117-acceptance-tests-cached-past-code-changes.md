# 117. The acceptance tests report a cached pass after the code they test has changed

**Open, in progress since 2026-10-18 in the session "item 117". Filed 2026-10-18 (r626), from what item 114 found. Nobody's call — a defect.**

`make test-acceptance` (`go test ./testing/acceptance/...` in `botropolis/Makefile`) reports `ok (cached)` after `pkg/render` and `pkg/app` have changed.
The acceptance package builds the binary it drives with `go build` in its `TestMain`, and imports neither package, so Go's test cache keys the result on files that do not include the code under test, and replays the last pass.
So every `make test` since the cache last held a pass may have skipped the acceptance tests entirely, while printing `ok`; item 114 checked its own slices with `go test -count=1`, which is how it saw this.
This is the shape `botropolis/CLAUDE.md` already names for the docs test: a cached test is a test that did not run.

CI runs on a fresh runner with no test cache, so CI's acceptance results are real; the gap is every local run, including every item session's "tests green" before landing.

## The fix

Make the cache see the binary's inputs, or bypass it for this package: `-count=1` on the acceptance target is the simple answer, at the cost of always running them; making the test depend on the built binary's content (opening the source tree or the binary so the cache records it, as the docs test does for its files) keeps caching honest when nothing changed.
Say which, and why.

Tests: change a file under `pkg/render` in a way an acceptance test sees, run `make test-acceptance` twice, and the second run must not report `(cached)`; mutated red on today's Makefile.

## Answered while building

- **The bar** (Aria, 2026-10-18, in item 114's window, relayed by its session): *"Acceptance tests need a new run every time unless the binary itself hasn't changed."* So a cached acceptance result is acceptable only when keyed on the built `botropolis` binary itself — the same binary, the same result — and otherwise the tests run again; `-count=1` on every run also meets it.
- **Targeted runs** (Aria, 2026-10-18, also relayed by item 114's session): *"But we may want to use filtering to run targeted acceptance test runs based on what we know was changed."* The import graph cannot choose the tests, since every acceptance test runs the same whole binary; coverage can. Build the binary with `go build -cover`, give each test its own `GOCOVERDIR`, record which packages each test touched (`go tool covdata pkglist`), and keep that map. The packages a change touches then choose the `-run` filter. A full uncached run is the fallback when the map is missing or stale, and says so when it falls back, and a full run refreshes the map.
