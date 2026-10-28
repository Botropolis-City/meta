# 318. Each nightfall keeps its lights: the city retains about 40 MiB per night, outside the Go heap

**Open, in progress since 2026-10-28 in the session "item 318". Filed 2026-10-28 (r1204), from item 308's light-cycle check, measured by its session and the performance manager. Nobody's call — a defect against the growth budget.**

On the 600-district fixture at r1197, with 180 s settled phases, a city held at day stays flat (454 → 453 MiB over 15 minutes), but one cycled by the clock goes day 445–448 → night 490 → day 485–488 → night 522–536 → day 531–541 MiB of `Private_Dirty`, in two runs.
Each nightfall adds 40–46 MiB and the following day gives back 3–5; only about 9 MB of each night is Go heap (`inuse_space` +7.2 MB), so about 31 MiB is outside it — most likely night's textures, the lit windows and the lights layer, made at nightfall and never released at daybreak.
After two nights it settles at 522–541 MiB, above the 512 MiB settled budget (approximate under llvmpipe, where textures count in `Private_Dirty`).

In use the light switches twice a day, so this is about 40 MiB a day for as long as the city stays open, against the growth budget of 1 MiB an hour; a soak pinned to one light (item 308) cannot see it.

## The fix

Release, or reuse, night's images at daybreak so a second night costs what the first did.
The test is item 308's slice 2, `testing/acceptance/lightcycle_test.go` (held in item 308's worktree): night → day → night → day, each repeat within 4 MiB of the first; it lands with this fix, red first, unchanged.
