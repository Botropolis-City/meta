# 326. A daemon started under the landing lock inherits the lock's descriptor, and holds it after the run dies

**Open. Filed 2026-11-02 (r1209), found by item 318. Nobody's call — a defect in the lock.**

A `make test-acceptance-locked` run of item 318's real-GPU cycle timed out on 2026-10-28, and its test daemon (`botropolisd` on a `/tmp` home) outlived it, reparented to `systemd --user`, with the open descriptor of `/tmp/botropolis-land.lock` it had inherited from `land-queue`.
It held the lock for four days: item 212's landing waited from 2026-10-29 until Aria killed the daemon by hand, since neither session may kill a pid it did not start.

## The fix

`tools/land-queue` opens the lock file close-on-exec (`O_CLOEXEC`), so no child of the locked command can inherit it; and `make land-queue` names the pid holding the lock when a wait passes a minute, so a stale holder is found at once rather than days later.
Tests: a child spawned under the lock holds no descriptor to it (checked through `/proc/<pid>/fd`); the wait message names the holder.
