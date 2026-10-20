# 165. A daemon test writes into the developer's real statistics store

**Open, in progress since 2026-10-20 in the session "item 165". Filed 2026-10-19 (r780), found while measuring 0.2.2 for the performance reports. Nobody's call — a defect.**

Depends on: nothing

On the Core Ultra 7 265U rig, the real `~/.local/state/botropolis/stats.db` held **124 transcript rows and one message, every one of them from a path under `/tmp/TestRunwhen_started_over_a_home_with_one_session…/`**, and nothing from the user's own 2.4 GiB of history.

The test is `TestRun`'s "when started over a home with one session" in `botropolis/cmd/botropolisd/main_test.go`.
It starts the daemon with `--home <temp dir>` and its own `--socket`, but leaves `XDG_STATE_HOME` alone, and `statedir.Default()` (`pkg/statedir/statedir.go`) takes the state directory from `XDG_STATE_HOME` or `os.UserHomeDir()`, not from `--home`.
So every `go test ./...` on a developer's machine writes the test's fixture session into the store the developer's own daemon reads, and anything else the daemon writes to its state directory goes the same way (unchecked for `groups.json` and `layout.json`).
`pkg/state/state_test.go` and the acceptance tests already isolate it with `t.Setenv("XDG_STATE_HOME", t.TempDir())`; this one does not.

**What it does to a user**: a developer's daemon starts on a store full of fixture rows, which is neither cold nor theirs, and the statistics on their map are someone else's until `markGone` and the ingest catch up.
It also made the A/B daemons in the 265U report start on a store with nothing real in it, so their start-up read the whole history: the report says so.

## The fix

1. The test sets `XDG_STATE_HOME` to a temp dir, as its neighbours do.
2. A guard so the next one cannot: a `TestMain` in every package that starts a daemon or opens a store, or one check in `statedir`, that fails a test run whose state directory is the user's real one.
   A guard is only worth having if it fails: mutate the fix away and watch it go red.
3. Ask whether `--home` should move the state directory too, since a daemon pointed at another home writing into this home's state is surprising outside tests as well.

Tests: the guard is the test; run `go test ./...` with `XDG_STATE_HOME` pointed at a directory the test watches, and assert nothing was written there.
