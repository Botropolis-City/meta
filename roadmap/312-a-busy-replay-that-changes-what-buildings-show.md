# 312. The busy replay changes no building's look, so it cannot reproduce a working city's cache churn

**Open, in progress since 2026-10-27 in the session "item 312". Filed 2026-10-27 (r1194), specified by the performance manager for item 212. Nobody's call — the tools need it.**

`perf.py replay HOME WRITERS SECONDS` appends one user line every 200 ms to each writer's transcript, which changes no look key, so a busy synthetic desk never re-bakes a look; item 212's hypothesis about the full-zoom redraw on Aria's city (working buildings' looks evicting still ones') could not be tested on it (performance manager, `7a3be58`).

## The fix

`perf.py replay --looks`, passed through by `perf-busy-city --replay-looks`, cycles each writer, at rates item 212 sets, through:

1. tool calls with their results, so a load starts and ends;
2. context rising across the thresholds that change courses and storeys, through assistant usage lines;
3. needs-you in and out;
4. working → resting → working.

Each line is written only to the scratch home's own staged transcripts: never through a symlink, never under `~/.claude`.
Done when a debug run on the synthetic desk at full zoom shows bakes after settling, with `changed=` naming those fields, and `perf_test.py` covers each kind of line.
