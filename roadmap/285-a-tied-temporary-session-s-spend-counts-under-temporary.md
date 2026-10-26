# 285. A temporary-directory session tied to a project still counts its spend under *Temporary*

**Fixed 2026-10-26 (`535f448`, r1128). Filed 2026-10-26 (r1122), the follow-up item 272 named. Nobody's call — a defect.**

Item 272 put a temporary-directory session tied to a project in that project's district on the map (`Session.District`, `city.SessionRoot`).
The statistics ranges still group spend by folder: `pkg/render/ranges.go`, the `stats.Filter` `Root` function and the ledger's `Window` are keyed by `city.ProjectRoot(cwd)`, so that session's building stands in the project while its spend counts under *Temporary* in the ranges and the breakdown.

## The fix

Key the ranges, the filter and the window by the session's district, `city.SessionRoot` (or `Session.District` when set), not `ProjectRoot(cwd)`.
Tests: a tied temporary session's spend counts under its project's district in the ranges and the breakdown; an untied one counts under *Temporary*; a project's totals equal the sum of the buildings drawn in it.

## Answered while building

- **The design** (session's, approved by the manager, 2026-10-26): a tie belongs to a session and the store keys spend by a message's folder, so no folder rule can tell a tied session from an untied one in the same folder; the ties travel by session id instead, as `stats.Filter.Tied`.
- **A gone transcript** (manager, 2026-10-26): a session whose transcript is gone has no `Session.District` left, so its spend goes back to *Temporary*. Acceptable, and said here and in the changelog.
- **Where the queries run** (session's correction, 2026-10-26): the manager asked for the daemon's benchmarks, against item 213's gate, but the daemon only ingests, which is unchanged; the views are read by the map, so the city's benchmarks were run instead.

## Closed

`535f448` (r1128) passes the city's ties by session id to every statistics view: `stats.Filter` gains `Tied`, and `Store.Window`, `Ledger.Window` and `Store.Districts` take it (`pkg/stats/tied.go`).
A message counts at the least of its tied sessions' districts, and at its own folder when none holds it, so a fork's copy counts once.
The ledger answers again when the ties change; the city hands them to the breakdown (`City.Ties`), and the ranges read them from the city and key their cache on them.
`pkg/stats/tied_test.go` covers each view, `Districts`, the store's and the live window and the ledger; the city's breakdown and the ranges' queries and cache key have their own; `testing/integration/city/tied_test.go` loads a home into a real store and holds each district's 24 h share and range total to the sum of the buildings drawn in it.
Each was mutated red: the city handing no ties, the live window ignoring them, the ledger not comparing them, the filter counting a tied message in its folder too, and the range key leaving them out.

Measured with a new `BenchmarkTiedViews`, on a machine at load average 35–50: a tied district's 3-month total costs about twice an untied read of the same rows, and a district with no ties about 1 ms more. The ranges read off the frame, every 30 s.

Deviations, for Aria:
- A tie arriving makes the ranges show *loading* once while they are read again, as changing the selection does.
