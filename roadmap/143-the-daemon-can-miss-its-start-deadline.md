# 143. The daemon can miss its 10-second start deadline on a large home, and exits

**Fixed 2026-10-19 (`bfc229e`, r740). Filed 2026-10-19 (r739), from validating the 0.2.0 release binaries. Nobody's call — a defect, and it blocks the AUR update.**

Depends on: nothing

Validating the released 0.2.0 binaries on Aria's machine (`~/.claude` about 2.1 GB, one live transcript of 365 MB, load average 15-20 while a demo film and a package build ran), `botropolisd` on a fresh state directory exited after exactly 10 s with **`botropolisd: context deadline exceeded`** in 3 of 6 starts tonight — once with `--stats=false` — and ran in the other 3.
The socket is up within 0.2 s; it is `app.Start` that times out: `startTimeout` is 10 s (`botropolis/pkg/appd/daemon.go`), and the `OnStart` hook runs a full `Rescan`, waits for the watch, and runs a second full `Rescan` (item 124), all inside it.
Each rescan re-reads every live transcript whole ([item 141](141-a-live-transcript-is-re-read-whole-on-every-change.md); 3.7 s of CPU for the 365 MB one when it was 339 MB), so two of them on a busy machine can take longer than 10 s.
An upgrade from 0.1.7 starts on a fresh statistics store, so this is the first start after installing 0.2.0. `Restart=on-failure` in `packaging/botropolisd.service` restarts it after 2 s, so it usually comes up on a later try, but the first start can fail, and a daemon started by hand or by the city just fails.

## The fix

Starting must not depend on how big the home is. The daemon is started once its socket is up and its first snapshot is served; the rescans that follow (item 124's second one) run after `Start` returns, not inside its deadline, and a slow first scan serves a partial or loading snapshot rather than failing the start. Keep the deadline for what genuinely must finish (binding the socket).
Item 141 is the deeper fix for slow rescans and stays its own item.

Tests: with a loader that takes longer than the start deadline (a fake that blocks), the daemon should start, serve a snapshot, and stay up; the second rescan still happens after the watch is up (item 124's test still passes); a measure test that `Start` returns within a bound independent of the home's size.
Then cut 0.2.1.

## Fixed

`Start` now only begins serving: the socket is bound before it, and the first scan, the watch and item 124's second scan run after it returns (`pkg/appd/daemon.go`).
Every request but a hook event waits for the first scan (`Daemon.HoldUntilLoaded`), so a client connecting early gets the full first snapshot, not a partial one.
Hook events are answered at once, because `botropolis-hook` is a synchronous Claude Code hook with a 5 s timeout and would otherwise hold up every tool call while a large home is read.
A failed first scan, which used to fail the start, shuts the daemon down with exit code 1, so `Restart=on-failure` still applies.

`pkg/appd/start_test.go` drives it with a loader whose first `Load` blocks: `Start` returns within a second while the scan is still running (red on the old code with `context deadline exceeded`), a hook event is answered during the scan, the snapshot served once it finishes holds the home's session, the daemon stays up, stopping mid-scan removes the socket, and item 124's test still passes.
Removing the hook exemption made one test fail, and removing the gate made another fail.

Deviation, agreed with the roadmap manager: no partial or "loading" snapshot is ever served.
No client has a read timeout — the city, bar, TUI, notify, `status`, `find`, `events` and `doctor` dial with a 500 ms connect timeout only — so clients simply wait for the first read.
The 0.2.0 binary exited 1 after the timeout, not 0; the 0 seen while validating came from the validation loop.

**After closing** (manager, 2026-10-19): CI failed on macOS at `bfc229e`: the new `pkg/appd/start_test.go` pointed `TMPDIR` at a test directory before making the socket's, so every case's socket path ran past macOS's 104 bytes — the fault item 130 fixed in the older test. Fixed in `e928e26` by making the socket's directory under the machine's own temporary directory, taken first; 0.2.1 is cut after it.
