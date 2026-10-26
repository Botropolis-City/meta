# 272. Every temporary directory becomes a district of its own

**Fixed 2026-10-26 (`3ed8d14`, r1122). Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — Aria ruled on what to do.**

Depends on: nothing
Landed: slice 1 (`b87d95c`, r1111).
Landed: slice 2 (`3ed8d14`, r1122).

A district is a session's working directory (`city.ProjectRoot`, `pkg/city/city.go`), cut back to the repository only for `.claude/worktrees/`.
A session in `/tmp/tmp.XXXX` or under `$TMPDIR` is a district of its own, so 489 sessions in temporary directories on Aria's other laptop made hundreds of one-building districts.

Aria, 2026-10-26: *"If anything in a tmp directory is tied to an existing district or session through its transcript, it should be part of that district. Everything else should fold into one single temporary district."*

## The fix

1. **Temporary** means a directory under `os.TempDir()`, `$TMPDIR`, `/tmp`, `/var/tmp` or macOS's `/var/folders` and `/private/var/folders`.
2. **Tied** means the session's transcript connects it to a session or district already on the map: a parent session (a subagent's or a spawned run's), a team or a peer message, or a temporary path that names a project — such as Claude Code's own scratchpad, `/tmp/claude-<uid>/<encoded project path>/<session>/scratchpad`. A tied session joins that district.
3. Every other temporary-directory session goes into **one district**, named for what it is, such as *Temporary*.
4. Tests, data-driven over each temporary root and each kind of tie, and over a non-temporary directory that merely contains `tmp` in its name, which stays its own district.

## Answered while building

- **The design** (session's, approved by the manager, 2026-10-26): slice 1 folds every temporary directory into one *Temporary* district in `city.ProjectRoot`, matching whole path segments, so `/home/u/tmp-project` stays its own; slice 2 ties a temporary session to a district by its transcript in the loader (team, parent, subagent visits, peer messages, file touches under a district's root as the weakest kind, and Claude Code's scratchpad matched against the districts on the map, since its path encoding is lossy), followed to a fixed point, strongest tie first. A tied session's spend still counts under *Temporary* in the statistics ranges until they follow its district, a follow-up filed at close.

## Closed

Slice 1 (`b87d95c`, r1111, released in 0.3.2) folds every directory under a temporary root into one district, *Temporary*, in `city.ProjectRoot`; `pkg/city/temporary_test.go` runs it over each root, at the root and nested, and over six directories that only contain `tmp` in their names.
Slice 2 (`3ed8d14`, r1122) sets `Session.District` in the loader (`state.AssignDistricts`, `pkg/state/districts.go`) for a temporary-directory session tied to a session elsewhere, and the city places it by that through `city.SessionRoot`.
The ties, strongest first: Claude Code's scratchpad for a project on the map, a lead of its team or subagents that worked in its folder, its team, a message either way, and files it edited under a project; ties are followed through other tied temporary sessions.
`pkg/state/districts_test.go` covers each tie, the chain, two districts and no tie; `testing/integration/state/districts_test.go` loads a home end to end. The unit test was mutated red (the ties' order, the fixed point), and the loader test failed until the loader called it.

Deviations, for Aria:
- A "spawned run's parent" has no record in a transcript, so the only parent evidence is a team's lead or subagents that worked in the session's folder.
- Three test fixtures (`testing/helpers`' week, journal and statistics ranges) and two unit tests stood their projects under the test's temporary home and now use invented `/home/user` paths.
- A tied session's spend still counts under *Temporary* in the statistics ranges, which group by folder; filed as a follow-up through the manager.
