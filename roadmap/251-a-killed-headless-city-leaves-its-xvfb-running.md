# 251. A headless city that is killed leaves its Xvfb running for good

**Fixed 2026-10-25 (`632258d`, r1046). Filed 2026-10-25 (r1033), found by the performance manager. Nobody's call — a defect.**

Depends on: nothing

On 2026-10-25, 83 idle `Xvfb` processes were running on the development machine, the oldest about 24 hours old, together holding about 8.9 GiB resident.
Every one was reparented to `systemd --user`, and every one named an `-auth` file in a directory that no longer exists: 77 under `/tmp/botropolis-state-*` (a headless city's private state directory, `privatePattern` in `botropolis/pkg/statedir/statedir.go`), 70 of them at the city's own 1600x900, plus five `botropolis-sheet-*` at 640x480 and one at the acceptance tests' 1100x760.

**The mechanism.** `xvfb.Start` (`botropolis/pkg/xvfb/xvfb.go`) runs Xvfb in a process group of its own (`Setpgid`) and relies on `Server.Close` to kill it.
A headless city (`pkg/app/module.go`) and `botropolis-demo sheet` call `Close` on a clean exit; a city killed outright — a test's cleanup, a timeout, `make land` interrupted — never does, so its Xvfb outlives it, its state directory is removed, and nothing can find it again.
Item 126 left no Xvfb behind among cities that exit; this is the path where the parent dies.

The cost is real on this machine: 8.9 GiB is memory every performance run measures beside, and display numbers run out after enough of them.

## The fix

Tie Xvfb's life to the process that started it: `Pdeathsig: SIGKILL` on Linux in `xvfb.Start`'s `SysProcAttr` (with the thread that starts it locked, since the signal follows the starting thread), and on other systems, where there is none, a watcher pipe Xvfb's side cannot outlive.
Keep `Close` as the clean path.

Tests: in `testing/integration/xvfb`, when the process that started an Xvfb is killed with SIGKILL, the Xvfb should be gone within a few seconds (polled, not slept); and a headless city killed with SIGKILL in an acceptance test leaves no `Xvfb` naming its state directory.
The 83 already running were started by tests and cities no session can name, so clearing them is Aria's to approve.

## Answered while building

- **The orphans already running** (Aria, 2026-10-25, asked by the manager): cleared. The manager killed the 77 whose parent was `systemd --user` and whose `-auth` directory no longer existed; five orphans whose directories still existed (four `botropolis-sheet-*` and one `TestRecordedClipKeepsTheScenesTime` temp directory, so those leak their directory too) and one with a live parent were left.

## Closed

Fixed in `632258d` (r1046).
On Linux, `xvfb.Start` gives Xvfb `Pdeathsig: SIGKILL`, and forks it from a thread locked to a goroutine that stays parked until `Close`, since the signal follows the thread that forked it (golang/go#27505).
`Close` is still the clean path.

Tests, each red before the fix and red again with `Pdeathsig` taken out:
`TestStartedBy` in `testing/integration/xvfb`, which SIGKILLs a process that started an Xvfb and polls for the server to be gone within ten seconds (it goes in about 0.2 s);
and `TestKilledHeadlessCity` in `testing/acceptance`, which SIGKILLs a recording `--headless` city and finds no `Xvfb` and no city process naming its state directory.

Deviations, both settled by the manager:

- **Linux only.** Other systems have no death signal, and Xvfb cannot watch a pipe itself, so a watcher would need a process between the city and Xvfb that nothing would ever run: the macOS CI job runs unit tests only.
  There, `Close` stays the only path, and `Start`'s doc comment says so.
- **The re-executed city child is not tied.** With only the child untied, the acceptance test stayed green in 500 ms, because the child exits by itself once its display is gone.
  A tie that no test could catch going missing would guard nothing (`botropolis/rules/a-green-test-is-not-a-guard.md`), so the test's third leaf checks the result, no child left, and `runHeadless`'s doc comment says why.

No changelog entry: `--headless` and `botropolis-demo sheet` are frame tooling, which release builds leave out.
