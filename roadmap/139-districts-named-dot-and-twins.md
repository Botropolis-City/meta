# 139. Sessions with no known folder make a district called ".", and two folders with one name are indistinguishable

**Open, in progress since 2026-10-19 in the session "item 139". Filed 2026-10-19 (r707), noticed during the validation checklist's run against main before 0.2.0. Nobody's call — a defect.**

Depends on: nothing

On Aria's machine on 2026-10-19 the sidebar's first district was named **"."**, holding two sessions whose record carries no working directory (`botropolis status --all --json` gives them `cwd: ""`): one removed with `claude rm` the day before, and one older.
`filepath.Base("")` is `"."`, so a session the city knows only from the statistics store or a record without a folder lands in a district named after an empty path.
Separately, two districts were both called **botropolis**: `~/workspaces/github/botropolis` (before the 2026-10-15 move) and `~/workspaces/github/botropolis-city/botropolis`; the sidebar, the map's labels and the City Plan show the same name for both.

## The fix

- A session with no known folder belongs to no district on the map; it is still counted in statistics, and if it must be shown, it is in a district named plainly ("folder unknown"), never ".".
- When two districts share a base name, each is labelled with as much of its path as tells them apart (`github/botropolis` and `botropolis-city/botropolis`), everywhere a district is named.

Tests: a session with an empty cwd → it should not make a district named "."; two roots with one base name → each label should differ, and each should end in the shared name.
