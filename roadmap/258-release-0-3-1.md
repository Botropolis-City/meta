# 258. Release 0.3.1

**Done 2026-10-26 (`d2bb5f2`, r1069; released from `0959e75`, r1071). Filed 2026-10-26 (r1067) at Aria's request. Nobody's call — Aria set the version, the soak waiver and what it waits for.**

Depends on: nothing

Aria, 2026-10-26, on the release after 0.3.0:
- *"if there is a leak now, it likely existed in 0.3.0, so let's finish up what we're working on and release without the soak. Then let's kick off the full 8hr soak. If we see a leak, that will be our first fix, and we'll release a patch version of just that."*
- the version: *"Until we hit 1.0.0, changes to the middle digit are major releases and changes to the last digit are both minor releases and patches. We'll follow true semver after 1.0.0."* Nothing since 0.3.0 breaks a user or a script (the Kenney packs that went were drawn by nothing), so this is **0.3.1**.
- it waits for [item 252](252-the-second-bridge-is-too-low-for-the-liner.md), the raised deck, and for [item 246](246-the-validation-checklist-predates-0-3-0.md)'s checklist.

Where it stands at filing: CI on `main` green ([item 254](254-the-metropolis-read-never-moves-on-ci.md)); `make test-performance` at r1066 within every budget but item 213's; the quiet pair of [item 212](212-every-frame-re-records-every-drawable.md) shows `main` drawing a frame in the same time as r954 at fit and 27% faster at full zoom.

## The release

Work down `botropolis/RELEASING.md`, with one change Aria made for this release only:
1. `VERSION` 0.3.1 and its `CHANGELOG.md` section; `make version-check`.
2. `make land`; CI green on that commit.
3. **Soak: waived for 0.3.1 by Aria**, and written so in the release's notes here; the full eight-hour soak runs on the released build afterwards (item 245's machine, `make run-soak`), and any growth over budget is filed as the first item of 0.3.2.
4. The checklist's steps left to Aria (item 246), against the release build.
5. Re-film the demo and website once (`make demo-adopt` first, since item 235 changed the shot key; the full re-film item 105's re-scrub causes; item 76's new media), and show Aria the three things item 76 left for her: the hero loop's crossfade seam, the 4:5 crop on a phone, and whether the site shows the views it does not import or the plain day.
6. The release workflow, `dry_run` first, then for real; then the AUR packages (`botropolis`, `botropolis-bin`).
7. Add Aria's pre-1.0 versioning rule to `RELEASING.md`, so the next release does not ask.

## Answered while building

- **Release now** (Aria, 2026-10-26, 03:45): *"Ok, let's just release now while I'm here. We can release without 252. Then we can kick off the soak now and re-release with these items if they're done and a good soak or with a fixed soak if it's not."* So 0.3.1 waits for neither 246 nor 252; the checklist's steps and the website re-film are skipped for 0.3.1 as the soak is, all three recorded in the release's notes here; the soak starts now, and 0.3.2 carries 246, 252 and whatever else is done, or the fix for a leak.
- **Item 252 joins** (Aria, 2026-10-26, once she had passed its frames: *"If 252 is done now, Why don't we include it in 0.3.1?"*): it lands on top of the version commit with its changelog line in the 0.3.1 section, and the release, the soak's build and CI's verdict all take that commit.
- **The checklist** (manager, 2026-10-26): item 246 put Aria's six steps (A1–A6) on the release path after 0.3.1's release run had started, so they were not run against 0.3.1; they are hers to run against it when she can, and they gate 0.3.2.

## Released

**0.3.1 was released on 2026-10-26 from `0959e75` (r1071), and it includes item 252.**
Aria delegated the release to the manager before she slept, so the real run and the AUR packages went out on the manager's go.

1. **The version** — `d2bb5f2` (r1069): `VERSION` 0.3.1, the `[0.3.1] - 2026-10-26` section with an empty `[Unreleased]` above it, and the pre-1.0 rule in `RELEASING.md`.
   `make version-check` passed, and `make land` landed it unchanged.
   CI was green on it: [run 40303398040](https://github.com/Botropolis-City/botropolis/actions/runs/40303398040).
2. **Item 252** landed on top of it as `c990b7d` and `0959e75` (r1071), with its changelog line in the 0.3.1 section.
   CI was green on `0959e75`: [run 40304700287](https://github.com/Botropolis-City/botropolis/actions/runs/40304700287).
3. **Dry run** from `0959e75`: [run 40306842989](https://github.com/Botropolis-City/botropolis/actions/runs/40306842989), green.
   The version resolved, CI's artifact was found, and the notes extracted.
4. **Release** from `0959e75`: [run 40307972869](https://github.com/Botropolis-City/botropolis/actions/runs/40307972869), green.
   It tagged [v0.3.1](https://github.com/Botropolis-City/botropolis/releases/tag/v0.3.1) at `0959e75` with 18 assets, and published the APT and RPM repositories and the Homebrew tap, both install-tested.
5. **AUR**: `botropolis-bin` 0.3.1-1 is AUR commit `98b6b87`, and `botropolis` 0.3.1-1 is `d102bcd`.
   Both PKGBUILDs dropped `kenney-packs.md`, which 0.3.1 no longer ships.
   Both were built locally and checked with namcap, the source package with its unit tests, and each `botropolis --version` reads 0.3.1.
6. **Skipped for 0.3.1, as Aria ruled**: the overnight soak, which runs on the released build afterwards; the checklist's steps for Aria (item 246); and the re-film of the demo and website.
