# 311. A recording city on six hundred districts never opens its map, and spends six cores waiting

**Open, in progress since 2026-10-27 in the session "item 311". Filed 2026-10-27 (r1194), found by item 308's light-cycle test. Nobody's call — a defect.**

`botropolis city --headless --record DIR --fps 1 --seconds 200 --script … --set light=live`, on its own daemon against the `bigHistory` fixture of `TestACityOfSixHundredDistricts` (270 days, 1,600 sessions, 600 projects), wrote no frame in 12 minutes and never printed *DRAWN the first frame*, while using about 586% CPU (61 CPU-minutes in 10 minutes).
The same fixture without `--record` draws its first frame within seconds.

A lead, not a cause: a `--screenshot` or `--record` run calls `scene.SetOpenOnRead(true)` (item 202), so the map opens only on a snapshot whose history is read (`HeftsRead`), and recording starts only once `scene.Opened()` (`held.go`).
The daemon's first read is paced (item 159); if it takes over 12 minutes here, or a recording city never sees `HeftsRead`, nothing is recorded.
The six cores spent while unopened are unexplained, and may be a second defect.

## The fix

1. Find why: capture the daemon's log, whether the first read finishes and when, and what the unopened city is spending its CPU on (a profile).
2. A recording city opens on six hundred districts within the stress city's own first-map bar, and an unopened city waits without spending cores.
3. A test on the stress fixture: a `--record` run writes its first frame within the bar.

Item 308's slice 2, the light-cycle check, waits on this.
