# 158. Group detection compares every pair of sessions again on every prompt in any session

**Open, in progress since 2026-10-21 in the session "item 158". Filed 2026-10-19 (r780), from the 0.2.2 performance reports. Nobody's call — a defect against the daemon budgets.**

Depends on: nothing
Landed: slice 1 (`76b01b8`, r875).

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

## As built (2026-10-21)

`group.Detector` keeps each pair's score, and each session's words and references, between runs.
It scores a pair again only when either session changed or the rarity of a word either uses moved.
**When the number of sessions changes, every pair is scored again**, because every word's rarity is `log(n/df)`.
That happens on a new session's first prompt, or when a session ages out of the 30-day window, and it is needed for the result to equal one from scratch.
`group.Detect` is a fresh Detector, and the tests hold each incremental result equal to it, including over a synthetic history replayed prompt by prompt (no real history is copied).

Two more per-run costs turned up besides the pairs.
The reference regexes ran over every prompt, and naming tokenised every member's prompts again; both are cached or cut short now.
And the loader parsed all of `history.jsonl` twice per load, once for grouping and once in `promptHistory`.
`claude.HistoryReader` now parses only the lines appended since the last read, and both reads share it.
It checks the bytes already parsed against a checksum, so a history that was replaced, cut short or rewritten in place, even at the same size, is read again whole.
It keeps everything in memory and writes nothing.

**The measure's limit**: the daemon's budget is 2% of one core, mean, with sessions working.
At one prompt every 5 s across the machine, that is 100 ms of CPU per prompt.
Half of that is kept for the rest of the load, so the load after a prompt gets 50 ms of process CPU (`testing/acceptance/group_cost_test.go`, median of five prompts with 100 sessions on the map).

**Before and after**, on the Ultra 7 265U with 100 sessions × 40 prompts, while other sessions loaded it:
`BenchmarkDetectAfterAPrompt` went from 55–100 ms to 7–10 ms (258 ms on the first synthetic shape),
and the load after a prompt went from about 150 ms to about 20 ms of CPU (157 ms with the fix reverted, which fails the measure).

**Live**, in a 300-second CPU profile of the daemon (`perf-pprof-build`, under `perf-daemon-ab` against the live `~/.claude` with item sessions working), `applyGroups` was **1% of the daemon's CPU**, down from 77% of its work outside the collector.
That build predates item 157 on main, so the collector was still half the profile.
The largest cost after it was `storedHefts.pass` at 18%, from globbing for transcripts (`claude.FindTranscript`) and reading hefts from SQLite.
That is not grouping, and it was reported to the roadmap manager rather than fixed here.
A 600-second `perf-daemon-ab` of main against this item, both without item 157, showed means of 23% and 20%, with the same bursts at the same moments: the bursts are not grouping.

Profile before and after with `perf-pprof-build` and `go tool pprof -top` on `/debug/pprof/profile?seconds=60`, with sessions working, and judge the result with `perf-daemon-ab`.
