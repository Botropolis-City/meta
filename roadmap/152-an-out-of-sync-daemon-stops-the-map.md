# 152. A daemon out of sync with the map stops it, with a choice to restart the daemon

**Open, in progress since 2026-10-19 in the session "item 152". Filed 2026-10-19 (r765) at Aria's request, from item 149's frame. Nobody's call.**

Depends on: 149 (slice 1)

Landed: slice 1 (`5cddccc`, r766).

[Item 149](149-what-1-0-0-promises.md)'s slice 1 (`89df7a6`, r760) exchanges a release and a protocol version on every request; on the manager's ruling a release mismatch only showed a strip chip, "daemon is 0.2.2, this is 0.2.3: restart it to update" (`botropolis/docs/screenshots/r760-item-149-daemon-notice.png`).
Aria, 2026-10-19, judging that frame: *"I think this is probably something that's worth preventing start. It could lead to unforeseen issues if they're not in sync. What if we prevent the whole thing from loading and instead show a popup menu stating they are out of sync. And asking the user to restart the daemon. Then we'll have two buttons that say "Exit" and "Restart Daemon". Exit will just exit the app. Restart Daemon will exit, restart the daemon and reload the app."*

## The fix

- **The map:** when the daemon's release or protocol differs from the map's, the city does not load; an in-window dialog (not a desktop popup: one window, any desktop) says they are out of sync and names both versions, with two buttons, **Exit** and **Restart Daemon**. Exit quits. Restart Daemon restarts the daemon the way it was started — `systemctl --user restart botropolisd` when the user unit runs it, otherwise stopping the old process and starting this build's `botropolisd` — waits for it to answer at the same release, and reloads the map in place (or re-executes itself), reporting plainly if the restart fails.
- **The strip chip** from slice 1 goes; a mismatch never reaches the map.
- **CLI commands** (`status`, `bar`, `tui`, `find`, …) refuse with one line naming both versions and how to restart the daemon; **hook events** stay lenient, so Claude Code is never blocked.
- macOS: the daemon there is not a systemd unit; restart it the way it is run there, and test what CI can.

Tests: a mismatched daemon → the map shows the dialog and draws no city; Exit → the process exits 0; Restart Daemon → the daemon is restarted (a fake service manager records the call) and the map loads once versions match; a failed restart → the dialog says so and stays; a CLI command against a mismatched daemon → non-zero with the line; a hook event → delivered. A frame of the dialog for Aria.
