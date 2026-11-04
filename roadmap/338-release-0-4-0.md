# 338. Release 0.4.0

**Open, in progress since 2026-11-03 in the session "release 0.4.0". Filed 2026-11-03 (r1246) at Aria's request. Nobody's call — Aria named the version and what it holds.**

Depends on: 333, 341
Landed: slice 1 (`cad2504`, r1256).
Landed: slice 2 (`8c908ea`, r1259).

Aria, 2026-11-02, through the design agent: *"I want this released asap as 0.4.0"*; and 2026-11-03, here: *"0.4.0 = 333 plus whatever has landed"*.

## What it holds

Item 333, *Tidying, part 1*, whole — it replaces the first-run screen, which is why the number is 0.4.0 under the pre-1.0 rule — plus everything on `main` when its candidate is cut: items 326, 328, 330, 331, 332, 334, 336, 337 and 212's slices as far as they have landed.
Nothing else waits to be in it.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.3.5 did (item 327): one candidate, a landing freeze from it to the tag, the soak with its cycle phase (item 321's real-box proof, which also closes item 321), the re-film, S1–S10, L1–L2, A1–A7, the dry run, the release, the AUR packages and the site.
Manual checks stand across a re-cut; automated ones re-run.

## Answered while building

- **The gate** (performance manager, 2026-11-03): `make test-performance` at `cad2504`, pinned and settled, everything met but `TestARescanAtTwoThousandSessions`, 16.6 ms against 16, which fails the same way at the previous main `3acddcf` (alternating runs 16.5 / 15.8 / 16.6 / 16.6): a drift since 0.3.4, item 340, not 0.4.0's code.
- **Aria, 2026-11-03:** the re-film passes (*"Pass, publish with 0.4.0"*); and *"Ship; soak now"* — 0.4.0 ships with the rescan check red, item 340 for 0.4.1, and the soak is ordered on the candidate.
- **Step 2** (release session): the package from CI 41660165080 with `SHA256SUMS` verified, S1–S10 pass, dry run 41663902297 green.
- **The checklist on the candidate package** (2026-11-03, 0.4.0-1 from `cad2504` installed): Aria ran A1–A7 and the tidy-up walk, all **pass**; L1 passes (58 agent records, 15 CLI records, 375 sessions, every live one agreeing); **L2 fails**: Claude Code 2.1.310 drops a stopped job outright and `botropolis rm` then gives up (item 341). Aria: *"Fix, re-cut, automated re-run"* — 341 lands as the freeze's exception, the candidate is re-cut, the automated checks re-run, the manual ones stand; the soak already running on `cad2504` counts, the fix being outside the city.
- **L1–L2 on the re-cut** (2026-11-03, 0.4.0-1 from `8c908ea` installed): L1 passes (377 sessions, every live one agreeing; the 1 blocked→waiting and 5 transcript-less jobs are by design);
L2 passes: a stopped session left the daemon and `claude agents --all` within 0.75 s of `botropolis rm` and stayed off across a daemon restart, and item 341's own case prints "Claude Code had already dropped it; forgetting it" and exits 0.
Released on that.
- **Released** (2026-11-03): run 41712826205 tagged `v0.4.0` at `8c908ea` and published 18 assets at 21:01 UTC;
the Homebrew tap's macOS 26 build was cancelled with no steps run (no runner within 15 min), so `publish-tap` was skipped, and the failed jobs were re-run on 2026-11-04.
The AUR packages are updated and committed locally (`botropolis` and `botropolis-bin`, "Update to 0.4.0"), the site media imported from the 0.4.0 film (52 images, 32 clips, no stand-ins);
the pushes and the media upload wait on 1Password after the machine rebooted at about 18:11 on 2026-11-03, which also ended the release, soak and item sessions.
- **The soak** was interrupted by that reboot: the cycle phase completed and reads pass on the heap, but the run's end is missing and the light switch is unproven; item 321 carries the record and a frame-per-phase slice.
