# 320. Release 0.3.4

**Open, in progress since 2026-10-28 in the session "release 0.3.4". Filed 2026-10-28 (r1204) at Aria's request. Nobody's call — Aria set what it waits for and what it runs.**

Depends on: 319
Landed: slice 1 (`d7ee4b6`, r1209).

Aria, 2026-10-28: *"let's plan and work towards 0.3.4 so we can release it asap. Sound like we just need 318, 319, a soak, a refilm, and then my checklist after that."*

## What it holds

Everything on `main` once item 315 has landed its last slice (item 318 turned out to be llvmpipe's growth, not the city's, so the release no longer waits on it): the tray (293), `c` attaching in the session's folder (302), the `light` setting (308, slice 1), the clinic's night windows (280), the truck at road speed (304), a recording city that opens on a big history (311), the opening's cost (315), and item 212's slices to that point.
Item 212 lands what is in flight by then; whatever is not landed then waits for 0.3.5.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.3.3 did:

1. The candidate: `VERSION` 0.3.4 and its changelog section, landed with `make land`; from that commit until the tag nothing else lands, so the soak, the film and the checklist all measure one build.
2. The soak, on the candidate, pinned to night (item 308), after item 319 so a failed pre-flight explains itself; it must pass the 1 MiB an hour budget, as the first 0.3.4 soak is the first to give a verdict at all (item 164).
3. The re-film, once, on the candidate, in parallel with the soak; Aria judges the sheets.
4. The validation checklist's scripted steps, then Aria's A1–A7 on the candidate package, A7 being the tray round trip (item 293).
5. The release workflow, `dry_run` first; the AUR packages; the website's media, purging the media host's cache after the upload (item 307).

## Answered while building

- **The whole-process switch check on a real GPU** (performance manager, 2026-10-28): item 318's windowed cycle at r1204 counts for 0.3.4 (333 / 339 / 339 / 340 / 340 MiB, both repeats within 1 MiB). Two render commits followed it, `9b5e96f` (no cracks below a quarter zoom) and `f5efb25` (backoff counters and the cap read), 49 lines in `pkg/render` touching nothing of night, lights, lamps or glows, so the run is representative by inspection of that diff; anything touching the lights before the tag needs a fresh cycle.
- **The candidate's checks** (release session, 2026-10-28): the scripted steps S1–S10 pass on `d7ee4b6`, each re-run alone with `-count=1` after `make land`'s own gate; the soak build is `~/.local/state/botropolis-perf/builds/soak-0.3.4-d7ee4b6`, and the package Aria installs is CI run 40794394136's `botropolis-0.3.4-1-x86_64.pkg.tar.zst`, its `SHA256SUMS` verified.
- **The release gate** (performance manager, 2026-10-28): `make test-performance` at `d7ee4b6`, quiet, every budget met: the recording city opens in 1.93 CPU-s against 2.5, the 600-district city fits at 14.39 ms against 16 with its live heap at 86–91 MiB against 150, and the daemon settles at 0.54–0.72%; raw in `~/.local/state/botropolis-perf/test-performance-r1209-d7ee4b6-release-0.3.4-20261028-184042/`.
- **The re-film** (film session, 2026-10-28): 46 of 46 shots filmed fresh from `d7ee4b6` in 30 minutes, 14 clips and 32 stills, every video decoding at its manifest's length; in `botropolis/.claude/worktrees/film-0.3.4/dist/demo`, for the release session to publish. Two flags, both already in 0.3.3's film: the hero loop's black wedge (filed as the item above this one in the series) and `layers/day.png` having no HUD, which is that shot's design.
- **Aria passed the re-film** (2026-10-29): *"Pass, publish with 0.3.4"*.
- **The soak** was ordered on 2026-10-29 at 00:56: server 3102814, the candidate build pinned to night.
- **The checklist on the candidate package** (2026-10-29, botropolis 0.3.4-1 installed): L1 and L2 pass (release session: 51 agent records, 13 CLI records and 327 sessions matched in one pass, every live one agreeing; a stopped valley session left `claude agents` and the daemon within 1.5 s and stayed off after a restart). Aria ran A1–A7, each **pass**, A7 being the tray round trip. Noted for an item: once, right after the daemon's restart, `botropolis status` printed *statistics are off: database is locked (SQLITE_BUSY)* on stderr while doctor said statistics ok.
- **The soak** (server 3102814, 2026-10-29, pinned to night, 8 hours): every budget met — city +0.39 MiB an hour visible and +0.17 hidden, daemon −0.03 and +0.01; stamped *not a measurement* only because the box's monitor state reads unknown (item 325). Aria, 2026-10-29: *"Release"*.
