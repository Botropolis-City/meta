# 336. Under `--home` without `--socket`, the read-only subcommands still read the real daemon

**Open. Filed 2026-11-03 (r1239), from item 334's close. Nobody's call — a defect, read-only.**

Item 334 made the city under `--home` without `--socket` touch only a daemon of its own, for packing, close-ups, demolition, the feed, loading, search and restart.
The read-only subcommands still read the default daemon under the same flags: `events`, `find`, `bar`'s live feed, `notify` and the TUI.
Nothing of the user's is written, but a staged home shows the real sessions, which is wrong and confusing in the same way.

## The fix

The same rule (`HomeSet && !SocketSet` means no daemon of its own) in each: read the staged home directly where the command can, otherwise refuse naming `--socket`; a data-driven test over the five that none reaches the default socket under `--home`.
