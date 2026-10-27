# 299. `make version-check` fails a landing on binaries left in `bin/` from before a version bump

**Open. Filed 2026-10-27 (r1179), seen twice: item 252's landing on 2026-10-26 and item 280's on 2026-10-27. Nobody's call — a defect in a guard.**

`tools/check-version` compares `VERSION` with what `bin/<binary> --version` reports, *if `bin/` has been built*.
In an item worktree, `bin/` holds whatever that worktree last built, often before a rebase brought in a version bump; so `make land`'s gate, which runs `make lint` and with it `version-check` before any rebuild, stops on "bin/botropolis: reports 0.3.2, VERSION says 0.3.3" although nothing is wrong.
Item 280's clinic fix for 0.3.3 failed its first landing that way tonight; item 252's had on 2026-10-26.

The check exists so that a release never ships binaries reporting the wrong version; a stale local build is not that.

## The fix

Check binaries only when they were built from the tree being checked: have `make build` write the commit it built from beside the binaries (`bin/.built-from`), and have `check-version` skip, and say it skipped, binaries built from another commit; or have the gate rebuild before checking.
Tests: binaries built from this commit with the wrong version fail; binaries built from an older commit are skipped and named; no `bin/` says so.
