# 285. A temporary-directory session tied to a project still counts its spend under *Temporary*

**Open, in progress since 2026-10-26 in the session "item 285". Filed 2026-10-26 (r1122), the follow-up item 272 named. Nobody's call — a defect.**

Item 272 put a temporary-directory session tied to a project in that project's district on the map (`Session.District`, `city.SessionRoot`).
The statistics ranges still group spend by folder: `pkg/render/ranges.go`, the `stats.Filter` `Root` function and the ledger's `Window` are keyed by `city.ProjectRoot(cwd)`, so that session's building stands in the project while its spend counts under *Temporary* in the ranges and the breakdown.

## The fix

Key the ranges, the filter and the window by the session's district, `city.SessionRoot` (or `Session.District` when set), not `ProjectRoot(cwd)`.
Tests: a tied temporary session's spend counts under its project's district in the ranges and the breakdown; an untied one counts under *Temporary*; a project's totals equal the sum of the buildings drawn in it.
