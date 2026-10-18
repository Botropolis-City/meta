# 117. The acceptance tests report a cached pass after the code they test has changed

**Open, in progress since 2026-10-18 in the session "item 117". Filed 2026-10-18 (r626), from what item 114 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`be84355`, r633).
Landed: slice 2 (`3603eb5`, r639).

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
- **Why not key on the binary itself** (item 117's session, 2026-10-18): `go test` decides whether to replay before `TestMain` runs, from the test binary's build ID, the environment and the size and modification time of files the last run opened, so it cannot know the binary a test will build. The fix is to make the acceptance package import every in-module package `cmd/botropolis` links, so their content-hashed build IDs key the test binary: any change to what the binary is built from reruns the tests, by any way of invoking them, and unchanged code still caches. A guard keeps that list complete, and `main.go`'s body moves to `app.Main()` so nothing the binary runs is outside the cache's view (manager, 2026-10-18).
- **Slices** (manager, 2026-10-18): 1, the import fix, tested in a scratch copy of the module, where a second unchanged run must be cached and a change under `pkg/render` must not be; 2, files only a subprocess reads — fixtures the binary opens and `tools/` scripts tests run — each opened by its test so the cache sees them, with a guard; 3, targeted runs from a coverage map.
- **As built, slice 1** (item 117's session, 2026-10-18): importing the packages was not enough. When the link inputs change, `go test` retries the cache with the test binary's content ID, and the linker drops code nothing in the test binary reaches, so a change to `app.Run`, which only `main` calls, still replayed a pass. So `testing/acceptance/binary_test.go` references `app.Main`, which is now all `main.go` calls, and the test binary links what the binary links. `TestTheCacheSeesTheBinary` changes `app.Run` and `render.Run` in a scratch copy, on the signature's own line, because a probe that adds a line shifts every later line number and changes the binary through its line table alone, which let a blank import pass. Mutated red without `binary_test.go`, and with a blank import in its place. It runs `go test -run '^TestStatus$'` there instead of `make test-acceptance` three times, because the Makefile line adds nothing the cache sees (manager, 2026-10-18).
- **As built, slice 2** (item 117's session, 2026-10-18): fixtures were already seen, since `LiveFixtureHome` and `stage()` read them in-process. `helpers.Tool` opens a `tools/` script and the `tools/` directory, so a sibling the script runs, such as `check_docs.py`, is in the key too, and the docs, demo and release-aliases tests take their paths from it. `demo_test` also opens `.publishable-tokens`, present or not. The packaging tests go-build the binary too, so they reference `app.Main` as well, and `shell_test` opens the shim bash sources, before any skip. Two guards parse the tests: no `exec.Command` names a `tools/` script except through `helpers.Tool`, and every package that go-builds `cmd/botropolis` references `app.Main`. Scratch-module probes cover the demo script, the shim and the packaging binary, each red before its fix (manager, 2026-10-18).
