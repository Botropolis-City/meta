# 324. Right after the daemon restarts, `botropolis status` says statistics are off because the database is locked

**Fixed 2026-11-02 (`fce7312`, r1214). Filed 2026-10-29 (r1209), from 0.3.4's checklist run (L1, the release session). Nobody's call — a defect, small.**

Once, seconds after `systemctl --user restart botropolisd`, `botropolis status` printed *botropolisd: statistics are off: database is locked (5) (SQLITE_BUSY)* on stderr, while `botropolis doctor` said statistics ok, and the next call was clean.
The stopping daemon and the starting one, or the starting one and a client, held `stats.db` at the same moment, and the busy error was reported as the statistics being off, which is a settled state, not a moment's contention.

## The fix

Open `stats.db` with a busy timeout so a locked moment waits rather than fails, and report *off* only when the database cannot be opened at all; a test that a lock held for less than the timeout does not turn statistics off.

## Closed

The busy timeout was already on `stats.db`'s connection string; it never applied.
The schema migration's deferred transaction read `user_version` and then wrote, and SQLite does not wait when a read must become a write, so a daemon starting while the stopping one still wrote got SQLITE_BUSY at once.
The migration now begins `IMMEDIATE`, on its own handle, so it waits out the timeout; the store's own transactions are unchanged, keeping item 110's test that an open read does not block a write.
`TestOpen` in `pkg/stats/store_test.go`: a write lock released within the timeout opens the store (red with this item's exact error, green after), and one held past it still refuses, naming the lock, as the manager asked.
