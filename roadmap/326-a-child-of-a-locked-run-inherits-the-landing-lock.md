# 326. A daemon started under the landing lock inherits the lock's descriptor, and holds it after the run dies

**Fixed 2026-11-02 (`18a8dd3`, r1231). Filed 2026-11-02 (r1209), found by item 318. Nobody's call — a defect in the lock.**

A `make test-acceptance-locked` run of item 318's real-GPU cycle timed out on 2026-10-28, and its test daemon (`botropolisd` on a `/tmp` home) outlived it, reparented to `systemd --user`, with the open descriptor of `/tmp/botropolis-land.lock` it had inherited from `land-queue`.
It held the lock for four days: item 212's landing waited from 2026-10-29 until Aria killed the daemon by hand, since neither session may kill a pid it did not start.

## The fix

`tools/land-queue` opens the lock file close-on-exec (`O_CLOEXEC`), so no child of the locked command can inherit it; and `make land-queue` names the pid holding the lock when a wait passes a minute, so a stale holder is found at once rather than days later.
Tests: a child spawned under the lock holds no descriptor to it (checked through `/proc/<pid>/fd`); the wait message names the holder.

## Closed

Fixed in botropolis `18a8dd3` (r1231), with `b492c23` (r1232) making the land acceptance tests seed every `tools/land-queue` source rather than `main.go` by name.
Go already opens files close-on-exec, so the descriptors were passed on purpose, through `cmd.ExtraFiles`, as flock(1) does.
That is gone: `land-queue` holds the lock and its ticket itself and passes the command neither, and on Linux the command gets SIGTERM (`Pdeathsig`) if `land-queue` dies, so it still cannot outlive the lock.
The holder is named in the wait message of `make land` and the other locked targets, not in `make land-queue`'s listing: a wait past a minute (`LAND_QUEUE_NAME_HOLDER_AFTER` in tests) prints every process with the lock open, by pid and command line.
`tools/land-queue/inherit_linux_test.go` shows it: a daemon started as `sleep 300 </dev/null >/dev/null 2>&1 &` holds no descriptor to the lock or the queue and the next landing goes through, a command whose `land-queue` is killed alone stops, and a long wait names the holder.
Each was red before the fix; the daemon case reproduced the four-day hold as a landing that never got the lock.
