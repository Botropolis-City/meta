# 251. A headless city that is killed leaves its Xvfb running for good

**Open. Filed 2026-10-25 (r1033), found by the performance manager. Nobody's call — a defect.**

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
