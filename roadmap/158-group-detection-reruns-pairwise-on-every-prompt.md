# 158. Group detection compares every pair of sessions again on every prompt in any session

**Open. Filed 2026-10-19 (r780), from the 0.2.2 performance reports. Nobody's call — a defect against the daemon budgets.**

Depends on: nothing

`Loader.applyGroups` (`pkg/state/groups.go:71`) re-runs `group.Detect` (`pkg/group/cluster.go:22`) whenever the stat key of `~/.claude/history.jsonl` changes, as well as when the sessions' signature or the groups file change.
`history.jsonl` is appended on every prompt in every session, so with sessions working, detection runs on nearly every load.
`Detect` builds edges between every pair of members (`detection.pair` → `Wording.Related`/`Shared`), so each run costs O(n²) in the sessions on the map, and `confirmLikely` can run it twice.

**What it costs**: in a 60-second CPU profile of the 0.2.2 daemon on the laptop, **77% of the daemon's work outside the garbage collector was group detection** ([the laptop report](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md), finding 4).
It is the largest cost left once item 157 stops the collector running continuously.

**The budgets it breaks** ([budgets.md](../performance/budgets.md)): daemon CPU ≤ 2% of a core mean and ≤ 25% at p95, measured with sessions working.

## The fix

Key the detection on what it actually reads, not on the file's stat: the prompts of the sessions that are members, and the signature it already computes.
A new prompt from one session changes only that session's pairs, so the pairwise scores can be cached and only the pairs involving a changed session recomputed, which makes a prompt cost O(n) rather than O(n²).
The clustering after the edges is cheap by comparison, and can run every time.

Tests: `Detections()` already counts runs, so a test can append to `history.jsonl` for a session whose wording does not change any edge and assert no full detection ran; a second that the groups found incrementally equal the groups found from scratch over a recorded history; and a measure test of CPU per prompt with 100 sessions on the map, whose limit is set from the budget.

Profile before and after with `perf-pprof-build` and `go tool pprof -top` on `/debug/pprof/profile?seconds=60`, with sessions working, and judge the result with `perf-daemon-ab`.
