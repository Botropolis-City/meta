# 152. A daemon out of sync with the map stops it, with a choice to restart the daemon

**Done 2026-10-19 (`a5789ba`, r775). Filed 2026-10-19 (r765) at Aria's request, from item 149's frame.**

Depends on: 149 (slice 1)

Landed: slice 1 (`5cddccc`, r766).
Landed: slice 2 (`cbf3497`, r772).

[Item 149](149-what-1-0-0-promises.md)'s slice 1 (`89df7a6`, r760) exchanges a release and a protocol version on every request; on the manager's ruling a release mismatch only showed a strip chip, "daemon is 0.2.2, this is 0.2.3: restart it to update" (`botropolis/docs/screenshots/r760-item-149-daemon-notice.png`).
Aria, 2026-10-19, judging that frame: *"I think this is probably something that's worth preventing start. It could lead to unforeseen issues if they're not in sync. What if we prevent the whole thing from loading and instead show a popup menu stating they are out of sync. And asking the user to restart the daemon. Then we'll have two buttons that say "Exit" and "Restart Daemon". Exit will just exit the app. Restart Daemon will exit, restart the daemon and reload the app."*

## The fix

- **The map:** when the daemon's release or protocol differs from the map's, the city does not load; an in-window dialog (not a desktop popup: one window, any desktop) says they are out of sync and names both versions, with two buttons, **Exit** and **Restart Daemon**. Exit quits. Restart Daemon restarts the daemon the way it was started — `systemctl --user restart botropolisd` when the user unit runs it, otherwise stopping the old process and starting this build's `botropolisd` — waits for it to answer at the same release, and reloads the map in place (or re-executes itself), reporting plainly if the restart fails.
- **The strip chip** from slice 1 goes; a mismatch never reaches the map.
- **CLI commands** (`status`, `bar`, `tui`, `find`, …) refuse with one line naming both versions and how to restart the daemon; **hook events** stay lenient, so Claude Code is never blocked.
- macOS: the daemon there is not a systemd unit; restart it the way it is run there, and test what CI can.

Tests: a mismatched daemon → the map shows the dialog and draws no city; Exit → the process exits 0; Restart Daemon → the daemon is restarted (a fake service manager records the call) and the map loads once versions match; a failed restart → the dialog says so and stays; a CLI command against a mismatched daemon → non-zero with the line; a hook event → delivered. A frame of the dialog for Aria.

## Answered while building

- **When the daemon is the newer one** (Aria, 2026-10-19, through the manager), the second button is **Restart Botropolis**, which runs the map again from its path on disk with its own arguments: restarting the daemon cannot help, since its unit already runs the new build.
- **The wording** (Aria, 2026-10-19, judging the r772 frames): the GUI is the city, as `botropolis city` calls it, so the dialog says *"The Botropolis city and its daemon must be running the same version. Please restart the daemon to continue."* (or *"the city"*), lists *Botropolis daemon version* and *Botropolis city version* in two aligned rows without chrome, and the newer-daemon button is **Restart City**; the commands and doctor say *"the Botropolis city and its daemon must be running the same version (daemon 0.2.1, city 0.2.2)"* and how to restart.
- **The manager's defaults** (2026-10-19): the city reloads in place rather than the map exiting and relaunching; Escape or q exits and Enter or r restarts, as well as the buttons; a dev build against a release daemon counts as out of sync; and it landed in two slices.
- **The manager's conditions:** a restart started by hand must never touch a process that is not the daemon on that socket, and refuses when the socket cannot say which process that is; the re-exec keeps the map's arguments.

## Closed

Slice 1 (`5cddccc`, r766) added `botropolis/pkg/daemonctl`, which asks the socket for its peer's process (SO_PEERCRED on Linux, LOCAL_PEERPID on macOS) and restarts that daemon the way it was started:
`systemctl --user restart botropolisd.service` when its cgroup names the unit, `launchctl kickstart -k gui/<uid>/homebrew.mxcl.botropolis` when the Homebrew job's pid is the peer, and otherwise SIGTERM to that one process and this build's `botropolisd` started with its old arguments.
It then waits for a daemon to answer at this build's release, and says plainly what went wrong when none does.
Its unit tests drive a fake service manager; an integration test restarts a real fake daemon on a scratch socket, with a service-manager runner that fails the test if called.

Slice 2 (`cbf3497`, r772) refuses any release or protocol apart everywhere but a hook's event, puts the dialog in place of the city, makes the commands refuse with one line and a hint, fails doctor's daemon check, and removes the strip chip.
Her wording landed in `a5789ba` (r775), and she approved its frames with the title as it is (2026-10-19).
Frames for Aria, `4fe6577`: [Restart Daemon](../botropolis/docs/screenshots/r775-item-152-out-of-sync-restart-daemon.png) and [Restart City](../botropolis/docs/screenshots/r775-item-152-out-of-sync-restart-city.png); the first wording's are r772.
The acceptance tests were mutated red: drawing the city anyway fails the frame-border check, and letting a release apart through fails all five commands.

Flagged for Aria: macOS is covered by unit tests and cross-compilation only, since CI cannot run a launchd job; and the restart is untested against a live systemd unit by design, so that no test touches her daemon.
