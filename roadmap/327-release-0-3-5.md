# 327. Release 0.3.5

**Done 2026-11-03 (`48f0cd9`, r1230; tagged v0.3.5). Filed 2026-11-02 (r1209) at Aria's request. Nobody's call — Aria chose what it holds.**

Depends on: 323, 294, 268, 259, 255, 324, 212 (slice 27), 307, 325, 321 (slice 1), 318, 308, 317, 322, 331
Landed: slice 1 (`e23414d`, r1227).
Landed: slice 2 (`48f0cd9`, r1230).

Aria, 2026-11-02: *"Quality patch, go with your list."*

## What it holds

A quality patch, in two halves.

Fixes people see: 323 (the hero loop's black corner), 294 (a building drawn small as its scaffold comes down), 268 (a first sighting behind a covering panel), 259 (a long boat and a raised deck), 255 (a road's vehicle names its traffic), 324 (`status` after a restart), and item 212's ground key, its last slice.

Release machinery, so the next release needs no hand steps: 307 (the media upload's cached not-found), 325, 321, 318 and 308's slice 2 (the soak: the monitor state, the light cycle on the box's real GPU, a day-night check llvmpipe cannot inflate), 317, 322 and 326 (`KEEP_ON_FAILURE`, perf tests under any open window, the landing lock leaking into children); then 164 closes, the soak having measured the budget.
Item 267 (the site's version typed by hand) joins when Aria stores the `SITE_DISPATCH_TOKEN`; it does not block.

Left for later, on purpose: 257, 261, 204, 245, the parked 238 and 277, and the blocked 96 and 296; 265 waits on Aria.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.3.4 did (item 320): one candidate, a landing freeze from it to the tag, the night soak with its verdict, the re-film, S1–S10, L1–L2, A1–A7, the dry run, then the release, the AUR pushes (Aria's, unless the permission rule changes) and the site.

## Answered while building

- **Item 326 defers to 0.3.6** (manager, 2026-11-03, under Aria's overnight leave): every other item had landed and 326, the landing lock's descriptor, was waiting on a permission prompt in its own window; it is tooling nobody using Botropolis sees, so the candidate was cut without it rather than lose the night.
- **Aria, 2026-11-03:** ship with the light-cycle check red on the reference machine (*"Ship with that check red"*), item 328 to fix the second-night step; the re-film passes (*"Pass, publish with 0.3.5"*). The candidate `652b892` (r1228) carries item 329 on `e23414d`; the package, S1–S10, CI and the dry run were green on it, and item 330 was filed from the fitted frame's one-off spike.
- **Aria, 2026-11-03, later:** item 255's frames pass (*"Clips look good. Pass!"*); and the soak runs after the release, not before (*"We can soak post-release"*), since the day's only auction box cost twice the usual.
- **Aria, 2026-11-03, on the checklist:** A1–A7 all pass on 0.3.5-1 (`652b892`), L2 passes, and L1 found item 331 (a session blocked on a permission prompt reads as working). Her ruling: *"Let's hold to fix it, but we shouldn't need to re-run the manual checks. Just automated ones."* So 331 lands as the freeze's exception, the candidate is re-cut, and only the automated checks (the gate, S1–S10, L1–L2, CI, the dry run) run again; A1–A7 and the re-film stand.
- **The final gate** (performance manager, 2026-11-03): `make test-performance` at `48f0cd9`, quiet, every budget met but the light-cycle check Aria ruled to ship with (second night +8 MiB against 4, images flat): fitted 14.75 ms, opening 1.92 CPU-s, settled daemon 0.54–0.82%; raw in `~/.local/state/botropolis-perf/test-performance-r1230-48f0cd9-release-0.3.5-20261102-110258/`.
- **The automated checks on `48f0cd9`** (release session, 2026-11-03): S1–S10, CI 41494702059 with `SHA256SUMS` verified, the dry run 41497504598, L2, and L1 against Aria's daemon with every live session agreeing, the permission-prompt one now needs-you (item 331 confirmed live). The release workflow was then run.

## Released

0.3.5 was tagged `v0.3.5` at `48f0cd9` (r1230) by release run 41505224978 on 2026-11-03, every job green once the macOS tap job, which GitHub never gave a runner the first time, was rerun on the same tag; APT, RPM and the Homebrew taps published with it.
The site's media went up the same day through item 307's upload, the road's caption following item 255, and the site deployed showing v0.3.5.
The AUR packages, `botropolis` `e94224a` and `botropolis-bin` `6ac4428`, were pushed by the manager at Aria's word (*"push those yourself"*).
Everything the item asked for ran on the candidate: S1–S10, L1–L2, A1–A7 (all pass), the re-film (pass) and the gate, with the light-cycle check red by Aria's ruling (item 328); the soak runs after the release, at her choice, and closes item 321.
Found on the way and filed: items 328, 329 (shipped), 330 and 331 (shipped); item 326 deferred to 0.3.6.
