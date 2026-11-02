# 327. Release 0.3.5

**Open, in progress since 2026-11-03 in the session "release 0.3.5". Filed 2026-11-02 (r1209) at Aria's request. Nobody's call — Aria chose what it holds.**

Depends on: 323, 294, 268, 259, 255, 324, 212 (slice 27), 307, 325, 321 (slice 1), 318, 308, 317, 322
Landed: slice 1 (`e23414d`, r1227).

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
