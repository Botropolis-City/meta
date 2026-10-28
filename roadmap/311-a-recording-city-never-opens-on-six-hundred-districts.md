# 311. A recording city on six hundred districts never opens its map, and spends six cores waiting

**Fixed 2026-10-28 (`1259a1e`, r1197). Filed 2026-10-27 (r1194), found by item 308's light-cycle test. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`1259a1e`, r1197).

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

## Answered while building

- **The cause** (item 311, 2026-10-27): not the daemon's read, which finished in 10 s, but a deadlock in the recording clock — a capture's first tick ran before any snapshot, painted nothing, and every later update waited on that paint; the unopened opening panel then drew uncapped on llvmpipe.
- **Pace the opening everywhere?** Only headless and capture runs; a window has vsync, and pacing the sweep Aria sees would change it (manager, 2026-10-27).
- **The bar for a recording's first frame?** `firstMapLimit`, unloosened, from city start to the first file; reporting on CI as the stress city does, items 303, 305 and 306 (manager, 2026-10-27).

## Fixed

A recording on the 600-district fixture deadlocked in its own clock.
A recording ticks only once its last tick is painted (item 113), and its first tick came before the daemon's first snapshot, so the city drew only its opening, painted nothing of the city, and every update after stopped at `startTick`.
The wait that takes snapshots without ticking (`holdUnopened`) ran only once a snapshot had been offered, so the snapshot was never taken, the city never opened, and the open ceiling never fired.
The daemon's read was not it: a probe saw `heftsRead` in under 10 s, and the daemon idle from then on.
The six cores were the opening, redrawn with no cap: Xvfb has no vsync, so llvmpipe drew it as fast as it could, about 5 cores, while the Go side took 1.5 more.

- `holdUnopened` now holds any capture that has ticked and not opened, and takes a daemon's out-of-sync notice there too, so item 152's dialog still films.
- A headless city or a capture draws its opening at most ten times a second; a windowed city is not paced, since its display already is.
- `TestARecordingCityOfSixHundredDistricts` (behaviour tier): no frame within its 2-minute hang bound before the fix, a frame in 4.4 s after.
  Unit tests in `pkg/render` hold the first tick before any snapshot, the out-of-sync case and the pacing, each seen red before its fix, and the opened city's pacing case turned red by moving the pace above its return.

**For Aria:** an existing test asserted the deadlock — a capture that had ticked with no snapshot "should not hold", written for item 152's dialog; it now sets the out-of-sync notice it was about, and the manager approved the change.

**Moved to item 315:** the fixed city writes its first recorded frame inside `firstMapLimit`, but spends 2.7 to 3.3 CPU-seconds getting there against the 1 CPU-second first-launch bar the performance manager set, and so does a plain headless city on the same fixture (2.55).
About 1.3 of it is the collector spiralling at the city's 300 MiB memory limit, with the live heap at 267 to 399 MB around the first frame, and about 1.4 is llvmpipe while the opening is up.
That test and the measurements went to item 315's session, which lands them.
