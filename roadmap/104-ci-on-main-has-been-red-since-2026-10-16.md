# 104. CI on main has been red since 2026-10-16

**Open, in progress since 2026-10-17 in the session "item 104". Filed 2026-10-17 (r558), from what item 103 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`99e7125`, r582).

The `ci` workflow in `botropolis/.github/workflows/ci.yml` last passed on main at `fc06ba0`, 2026-10-16 07:30 UTC; 59 of the 60 runs since have failed, so a red run has stopped meaning anything and every item lands on top of it.
Item 103's `test-lint` job is green; three other things are not.

## What fails

1. **`test-macos`, both runners**: `TestFinderActs` ("and Ctrl+Y is pressed", including "and the directory has a space in it") and `TestOverlayStack` ("when nothing is open / and Ctrl+K is pressed / it should open the finder") in `botropolis/pkg/render` fail on macOS and pass on Linux.
   Item 82 made the finder's chords ⌘ on macOS, so the tests most likely press Ctrl where the Mac build listens for ⌘; the fix is to press the platform's modifier in the test, not to change the keys.
2. **`bench`**: the Benchmark step is killed with exit code 143 about a minute and a half in, so it times out or is cancelled rather than reporting a regression; find what grew (item 94's whole reads and item 91's measures both landed since) and either make it fit or give the step the time it needs, saying which.
3. **A flaky integration test**: `testing/integration/demo`'s `TestStagedHomeLoadsAsTheScenarioSays` ("when the home is unstaged / it should leave no session alive") failed once in six runs on a clean main checkout (item 103's session, 2026-10-17). A test that fails one time in six is a race in the test or in unstaging, and is found, not retried.

## Done when

Three consecutive `ci` runs on main are green, and the flaky test passes fifty runs in a row locally (`go test -count=50`).
