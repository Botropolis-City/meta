# 133. The lint test fails when two sessions run the tests at once

**Open, in progress since 2026-10-19 in the session "item 133". Filed 2026-10-19 (r678), from items 78 and 99. Nobody's call — a defect.**

Depends on: nothing

Item 129's `TestLintChecksFormatting` (`botropolis/testing/acceptance/format_test.go`) runs golangci-lint on a scratch copy of the module.
golangci-lint takes a lock for the whole machine, so when two item sessions run `make test` at once the probe can fail with *"parallel golangci-lint is running"*, and `it_should_name_the_file` goes red with nothing wrong.
Items 78 and 99 each hit it on 2026-10-19 and passed on a rerun; with several item sessions testing in parallel, which is now the normal case, it will keep happening, and a test that fails for nothing teaches everyone to rerun rather than read.

## The fix

Run the probe's golangci-lint with `--allow-parallel-runners` (or its own `--allow-serial-runners` wait), and give it its own cache directory under the scratch copy (`GOLANGCI_LINT_CACHE`), so it neither fails on nor waits for another run's lock; `make lint` keeps its own behaviour.

Tests: hold golangci-lint's lock from the test (start a long run, or take the lock file) and run the probe beside it → it should still name the unformatted file; mutate red by removing the flag.
