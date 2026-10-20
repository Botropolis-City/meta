# 165. A daemon test writes into the developer's real statistics store

**Fixed 2026-10-20 (`19fc029`, r798). Filed 2026-10-19 (r780), found while measuring 0.2.2 for the performance reports. Nobody's call — a defect.**

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

## Fixed

`19fc029` (r798), with its changelog entry after it.

1. `TestRun` in `cmd/botropolisd` points `XDG_STATE_HOME` at a temp dir, as its neighbours do.
2. **The guard is `statedir.Check(path)`.**
   In a test binary it panics, naming this item, when a path is the state directory the run started with or anything under it.
   `statedir.Dir()` calls it, so every store is covered — ledger, close-up, groups, layout, statistics, and any store added later — and so do the two writers under `Default()`, `claude.Summarise` and `RefreshUtilization`, before they make their directories.
   It is one check in `statedir` rather than a `TestMain` per package, so a package nobody has written yet is covered too.
3. **A daemon pointed at a home opens no statistics store** (manager's ruling, option A): the rule items 86 and 87 already applied to its ledger, close-up and groups.
   Its hefts come from whole reads, as with statistics off.

**Deviation, approved by the manager:** the guard sits on `Dir()` and the writers, not on `Default()` as first planned.
On `Default()` it failed about 55 tests in 9 packages, and only two of them touched a store.
The rest compute the usage probe's and the summaries' paths in `state.Build` to fence those transcripts out, and computing a name reads nothing.
So `Default()` stays an unguarded resolve, and a new writer under it must call `Check`.
Nothing enforces that, because a grep test would be a string match on code (`botropolis/rules/a-green-test-is-not-a-guard.md`).

The guard flushed out two more tests, each now isolated: `pkg/app` `TestRunExitCodes`, through the ledger path, and `pkg/render` `TestStatsPrompt`, which opened the real `stats.db` for its ledger.

**Mutations**, each run with `XDG_STATE_HOME` on a watched temp dir:
dropping the `cmd/botropolisd` Setenv and option A together panics that package through the guard, and the watched dir stays empty;
dropping the Setenv alone stays green, because option A already keeps a `--home` daemon out of statistics, so the Setenv is belt and braces rather than the guarded line;
turning the guard off fails `TestGuard` and `TestWritersCheckTheStateDirectory`, and the watched dir gains `botropolis/usage-probe` and `botropolis/summary`;
dropping option A fails `TestStatsWiring` "when the daemon was pointed at a home".
The item's hand check, `go test ./...` with `XDG_STATE_HOME` on an empty watched dir, left it empty.
The acceptance package timed out there under go's default ten minutes (item 131), and it isolates its own environment anyway.

**For Aria:** the 124 fixture rows are still in the real `stats.db` on this machine (one message, `msg_01`, and session `08b1d655…`), and the same is reported on the 265U rig.
The fix stops new ones and removes none, and nothing here touched them; the manager is offering a cleanup separately.
