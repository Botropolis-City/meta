# 272. Every temporary directory becomes a district of its own

**Open. Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — Aria ruled on what to do.**

A district is a session's working directory (`city.ProjectRoot`, `pkg/city/city.go`), cut back to the repository only for `.claude/worktrees/`.
A session in `/tmp/tmp.XXXX` or under `$TMPDIR` is a district of its own, so 489 sessions in temporary directories on Aria's other laptop made hundreds of one-building districts.

Aria, 2026-10-26: *"If anything in a tmp directory is tied to an existing district or session through its transcript, it should be part of that district. Everything else should fold into one single temporary district."*

## The fix

1. **Temporary** means a directory under `os.TempDir()`, `$TMPDIR`, `/tmp`, `/var/tmp` or macOS's `/var/folders` and `/private/var/folders`.
2. **Tied** means the session's transcript connects it to a session or district already on the map: a parent session (a subagent's or a spawned run's), a team or a peer message, or a temporary path that names a project — such as Claude Code's own scratchpad, `/tmp/claude-<uid>/<encoded project path>/<session>/scratchpad`. A tied session joins that district.
3. Every other temporary-directory session goes into **one district**, named for what it is, such as *Temporary*.
4. Tests, data-driven over each temporary root and each kind of tie, and over a non-temporary directory that merely contains `tmp` in its name, which stays its own district.
