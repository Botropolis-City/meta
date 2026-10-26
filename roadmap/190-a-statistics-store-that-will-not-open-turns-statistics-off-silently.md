# 190. A statistics store that will not open turns statistics off without a word

**Open, in progress since 2026-10-26 in the session "item 190". Filed 2026-10-21 (r844), found on the Core Ultra 7 265U rig while cleaning up after item 165. Nobody's call — a defect.**

Depends on: nothing

`statsSource` (`botropolis/pkg/appd/daemon.go`) opens the statistics store once, when the daemon builds its loaders, and when `stats.Open` returns an error it returns `nil`.
The daemon then runs with statistics off: hefts come from whole reads, nothing is written to the store, and nothing says so.
There is no log line, `botropolis doctor` has no statistics check, and the map shows no notice.

**It happened.** On the 265U rig, the real `stats.db` was a file at schema version 3 with no `meta` table; its copy from before item 165's fixture clean-up lacked it too, so the file was written that way, probably by a test run from a build of item 116 before it was finished.
`Store.migrate` reads `user_version` as 3, which equals `Version`, and then fails in `setMeta` with "no such table: meta".
So from the upgrade to 0.2.2 on 2026-10-19 until 2026-10-21, the 0.2.2 and then 0.2.3 daemons ran with statistics silently off.
The evidence: the daemon held no descriptor on the file, and the file was still in rollback-journal mode, which `Open` switches to WAL on every successful open.
Removing the file and restarting the daemon built a fresh store (182 transcripts, 21,812 messages) at once.

**The same path silences what item 149 promised.**
Item 149 made a store written by a newer build "refused by name", and `migrate` does build that error ("… cannot read: update Botropolis"); `statsSource` throws it away.
So the refusal 1.0.0 promises reaches nobody, and a user who downgrades loses statistics without being told why.

This is the silent-fallback pattern the meta `CLAUDE.md` describes for the docs guard: a fallback is a way to pass, and one that reads exactly like the healthy path is the fault.

## The fix

1. `statsSource` logs the error from `stats.Open`, naming the file, on the daemon's stderr, which the journal keeps.
2. The daemon reports the store's state over the protocol — open, off by setting, or refused with the reason — and `botropolis doctor` adds a `statistics` row that is `warn` with the reason when the setting is on and the store is not open.
3. The map shows a notice when statistics are on but the store was refused, as it does for a daemon of another release (item 152), with the file's path and what to do: update Botropolis for a newer store, or move the file aside for a damaged one.
4. Decide what a damaged store at the current version should do — refuse and say so, or repair a missing `meta` table — and record the choice in item 149's terms: a file is never reset or lost without the user's say.

Tests: a daemon started over a `stats.db` at `user_version` 3 without `meta` logs the error and reports the store refused; `doctor` warns for it; a store from a newer build produces the "update Botropolis" reason end to end, not only from `migrate`.
Mutate the logging and the report away and watch each test go red.

## Answered while building

- **A damaged store at the current version** (manager, 2026-10-26, from fix 3's "move the file aside" and item 149's rule that a file is never reset or lost without the user's say): refused, not repaired. A store at this version whose `meta` cannot be read is `ErrDamaged`; nothing on disk changes; the reason names the file and says to move it aside, and the read-only reader refuses it too, so the map agrees with the daemon. A repair would write into a store that may be half-built, which is the silent fallback again.
- **The plan** (manager): approved in three slices: typed refusals from `migrate` and `OpenReader` with the daemon logging each once; the store's state on every snapshot and the peer answer (omitempty, no protocol bump) and a `statistics` row in `doctor`; a dismissible notice on the map, its frame for Aria.
