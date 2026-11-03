# 336. Under `--home` without `--socket`, the read-only subcommands still read the real daemon

**Fixed 2026-11-03 (`01dcc84`, r1243). Filed 2026-11-03 (r1239), from item 334's close. Nobody's call — a defect, read-only.**

Landed: slice 1 (`01dcc84`, r1243).

Item 334 made the city under `--home` without `--socket` touch only a daemon of its own, for packing, close-ups, demolition, the feed, loading, search and restart.
The read-only subcommands still read the default daemon under the same flags: `events`, `find`, `bar`'s live feed, `notify` and the TUI.
Nothing of the user's is written, but a staged home shows the real sessions, which is wrong and confusing in the same way.

## The fix

The same rule (`HomeSet && !SocketSet` means no daemon of its own) in each: read the staged home directly where the command can, otherwise refuse naming `--socket`; a data-driven test over the five that none reaches the default socket under `--home`.

## Closed

`events`, `find`, `bar`'s live feed, `notify` and the TUI now take `ownSocket`, as the city does since item 334.
The snapshot reader, the shared live feed and `find` read the staged home directly when there is no socket, without the "not reachable" notice; `events`, whose log lives only in a daemon, refuses naming `--socket`.
Tested in `pkg/app/home_subcommands_test.go`, data-driven over the five against a fake daemon at the default socket: under `--home` without `--socket` none reaches it, and with `--socket` each asks the home's own.
The TUI is tested through the feed it follows, `services.feed`, since running the terminal UI in a test is not practical.
