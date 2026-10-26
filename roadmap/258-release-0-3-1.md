# 258. Release 0.3.1

**Open, in progress since 2026-10-26 in the session "item 258". Filed 2026-10-26 (r1067) at Aria's request. Nobody's call — Aria set the version, the soak waiver and what it waits for.**

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
