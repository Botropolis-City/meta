# 354. Release 0.5.0

**Open, in progress since 2026-11-07 in the session "item 354". Filed 2026-11-06 (r1266) at Aria's request. Nobody's call — Aria named what it holds; she confirms the number when the candidate is cut.**

Depends on: 340, 348, 349, 350, 351, 352, 353, 359

The second half of the split recorded on [item 349](349-release-0-4-1.md): Aria, 2026-11-06, *"Do the split, but let's not soak until after 0.5.0"*.

## What it holds

- Item 348, neighbourhoods and the form of a group's line, judged on frames.
- The controls redesign, items 350 to 353, *Controls, parts 1 to 4*, which Aria asked for in the next release through the design agent.
- Item 359, a grouped building lighting its whole group under the pointer (Aria, 2026-11-06).
- Item 340, the rescan drift that 0.4.0 and 0.4.1 shipped red; it wants a quiet machine, so it runs once the item sessions thin out.

Aria named 0.5.0 when she chose the split; under the pre-1.0 rule a 0.X is for a breaking change, and whether the controls redesign is one is hers to confirm at the cut, so the number is written here as she said it.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.4.0 did (item 338): one candidate, a landing freeze from it to the tag, the re-film, S1–S10, L1–L2, A1–A7, the dry run, the release, the AUR packages and the site.
**The soak runs after this release** (Aria, 2026-11-06), once, on the released build, and stands for 0.4.1 too, whose soak she waived; its record and verdict go here, and a verdict over budget is a new item against 0.5.1.

## Answered while building

- **Item 340 starts once 0.4.1 is tagged** (Aria, 2026-11-06): it wants a quieter machine than tonight's, and it compares the rescan's profile at r1209 with now, so both are measured under the same load.
- **Tagged overnight on the automated checks** (Aria, 2026-11-07, before bed): *"Tag on automated checks, like 0.4.1"* — A1–A7 are waived as they were for 0.4.1, and the release tags when every automated check is green, the rescan check included now that item 340 has brought it to 12.2 ms against 16.
  The AUR packages are pushed on her standing approval, given for 0.4.1 and renewed here; the site's media upload waits for her 1Password.
- **The performance gate runs on the performance profile** (Aria, 2026-11-07): set again that night, since the machine had gone back to balanced; the gate records the profile, RAPL limits and governor beside its numbers, as item 358 asks, and a red reading on any other profile is not a measurement.
- **The soak still runs once, after the tag**, as ruled on 2026-11-06.

## The checks

- **The candidate** (release session, 2026-11-07): `b5d2d46e` (r1331), `VERSION` 0.5.0 and a `[0.5.0]` section gathering everything that was under `[Unreleased]`, landed through `make land` with its whole gate green, S1–S10 included.
- **CI** 42377323663 green on its first attempt, both macOS runners included; eight packages, amd64 and arm64, verified against `SHA256SUMS`, the binaries reporting 0.5.0.
- **The performance gate**, every check green, the rescan included, after `settle` waited 7m42s: platform profile performance, governor powersave, EPP balance_performance, turbo on, RAPL long-term and short-term 57 W, peak 106 W, the same before and after (item 358).
  The rescan at 2,000 sessions 11.8 ms median against 16 (11.1–12.4, one outlier at 25.7); the fitted 600-district frame 14.6 ms against 16, zoomed 5.7 and panned 5.6 against 10; the 2,400-session city settled at 473 MiB under 512; the daemon at 2,000 sessions 59 MiB under 64.
  Skipped by design: `TestCalibrateCoreRate`, run by its own tool, and `TestLightCycleOnARealGPU`, which needs a window on Aria's screen.
- **L1–L2, side by side**, as 0.4.1's: the candidate's daemon on its own socket, config copy and state, cache and runtime directories, reading the real `~/.claude`; no sudo, and Aria's daemon left alone.
  L1 passes: 403 sessions, 55 jobs, 7 live records, each agreeing, and every finished job with no live process resting; a design-agent record saying idle over an unanswered prompt shows needs-you, as item 250 ruled, and the daemon read past a NUL-filled line in that transcript.
  L2 passes: a stopped throwaway session left `claude agents --all` and the daemon 7 s after `botropolis rm`, and stayed off across a restart of the side daemon.

## Released

- **Released** (2026-11-07): run 42384836569 tagged `v0.5.0` at `b5d2d46e` (r1331) and published 18 assets at 15:37 UTC, with the package repositories and the Homebrew tap, both macOS runners included, green.
  The dry run, 42382227091, was green at the same commit.
  The candidate is one commit: VERSION and the [0.5.0] section, which gathers everything under [Unreleased].
  It landed through `make land` with S1–S10 in its gate, and its CI, 42377323663, was green on the first attempt.
  The amd64 and arm64 packages matched `SHA256SUMS`, and their binaries report 0.5.0.
- **The checks** are recorded above: the performance gate on `performance`, every check green, the rescan included, and L1–L2 run side by side.
- **The re-film**: `make demo-media` at `b5d2d46e` filmed 51 shots in 80 files.
  It went to Aria with a contact sheet of its 52 stills, and her pass is pending.
- **The AUR** (2026-11-07): `botropolis` `59304e6..29d79b8` and `botropolis-bin` `5190213..fbd0e03`, both 0.5.0-1, their sources checked against the release, and pushed by the roadmap manager on Aria's standing approval.
- **The site**: the re-film's 52 images and 32 clips were imported in botropolis.city's `4b2663f`, committed but not pushed.
  Aria uploaded the clips on 2026-11-07, and `4b2663f` was pushed, but its CI failed on the Glance hotspots, so 0.5.0's page has not deployed; [item 360](360-the-website-still-describes-the-city-of-0-3-0.md) fixes that first.

Deviations, all ruled by Aria: A1–A7 were waived; the tag rests on the automated checks alone; and L1 and L2 ran against a candidate daemon beside hers.
The soak runs once, on the released build, and its record goes here.
Aria cut 0.5.1 for the group move fixes (2026-11-07), so the soak runs once, on 0.5.1 ([item 366](366-release-0-5-1.md)), and this item closes on the release alone.
