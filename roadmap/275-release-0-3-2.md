# 275. Release 0.3.2

**Done 2026-10-26 (`aefd89b`, r1116; tagged v0.3.2). Filed 2026-10-26 (r1109) at Aria's request. Nobody's call — Aria set what it holds and what it skips.**

Depends on: 272 (slice 1)

Aria, 2026-10-26, after 0.3.1 froze on her other laptop (items 270 to 274): *"Let's get this urgent issue fixed and into a release asap. Let's not wait for a soak or video for it. Whatever is in with it, we'll release as 0.3.2, but everything else we had planned for 0.3.2 can go into 0.3.3"*.
And: *"yes, you can run the candidate on 0.3.2 on my work laptop before tagging it."*

## What it holds

Whatever `main` holds when item 272's slice 1 lands: the freeze fixes (items 270's slices 1, 2, 3 and 5, 271's slice 1, 272's slice 1, 274), and everything already in `[Unreleased]` (items 213, 190, 263, 264).
Items 273 and 271's slice 2 go in if they land first; nothing waits for them.

## Steps, from `botropolis/RELEASING.md`, with Aria's waivers

1. `VERSION` to 0.3.2 and `CHANGELOG.md`'s `[Unreleased]` becomes `[0.3.2] - <date>`, with every user-visible change of items 270 to 274 in it; `make version-check`; land with `make land`, and let CI finish.
2. **Landings hold** from the bump until the release is tagged, since the release workflow tags `main`'s head.
3. The performance manager's `make test-performance` at the bump's commit must pass; it starts by itself when `VERSION` reads 0.3.2 on `main`.
4. The candidate is run on Aria's other laptop, over ssh, by the manager: its own daemon on its own socket, a temporary directory, nothing installed; it must open, draw a sensible number of districts, pan and quit. Nothing from that machine is named in any public file.
5. **Waived for 0.3.2 by Aria:** the soak (step 4), the re-film (step 6). The checklist's A1 to A6 (step 5) is not run, as for 0.3.1; all three run for 0.3.3.
6. The release workflow, `dry_run` first, then for real; then the AUR packages, with the `aur-update` skill.

## Answered while building

- **The candidate on Aria's other laptop** (manager, 2026-10-26, at `aefd89b`; its own daemon on its own socket, state and cache in a temporary directory, nothing installed, everything removed afterwards): the daemon served 723 sessions; the city, run in a virtual display because the laptop's screen was locked, drew its first frame 2.6 s after starting, with 24 districts where 0.3.1 made 559; a keyboard pan changed the frame; and a 15 s recording drew all 150 frames. Opened on the real screen it drew nothing, correctly, since the locker held the input focus, so `q` then `y` was not tried by hand there; item 270's quit fix is held by its test. A 0.3.1 city started on the same laptop earlier sat at a full core and 5.5 GB resident for 80 s.

## Released

0.3.2 was tagged `v0.3.2` at `aefd89b` (r1116) by release run 40400792045, after a dry run (40399396881); CI on that commit was green on every job, and the performance manager's `make test-performance` there met every budget.
APT, RPM and the Homebrew tap published from it; the AUR packages are `botropolis` `36dadcd` and `botropolis-bin` `af3989a`, both built here first, the source package's `check()` passing on a real config.
Waived by Aria for this release only: the soak, the re-film and the checklist's A1 to A6, which all run for 0.3.3.
