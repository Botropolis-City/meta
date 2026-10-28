# 312. The busy replay changes no building's look, so it cannot reproduce a working city's cache churn

**Done 2026-10-27 (`b735968`, r1149 of meta). Filed 2026-10-27 (r1194), specified by the performance manager for item 212. Nobody's call — the tools need it.**

`perf.py replay HOME WRITERS SECONDS` appends one user line every 200 ms to each writer's transcript, which changes no look key, so a busy synthetic desk never re-bakes a look; item 212's hypothesis about the full-zoom redraw on Aria's city (working buildings' looks evicting still ones') could not be tested on it (performance manager, `7a3be58`).

## The fix

`perf.py replay --looks`, passed through by `perf-busy-city --replay-looks`, cycles each writer, at rates item 212 sets, through:

1. tool calls with their results, so a load starts and ends;
2. context rising across the thresholds that change courses and storeys, through assistant usage lines;
3. needs-you in and out;
4. working → resting → working.

Each line is written only to the scratch home's own staged transcripts: never through a symlink, never under `~/.claude`.
Done when a debug run on the synthetic desk at full zoom shows bakes after settling, with `changed=` naming those fields, and `perf_test.py` covers each kind of line.

## Closed

`perf.py replay --looks`, and `perf-busy-city --replay-looks`, landed in `b735968`; the plain user-line replay stays the default, and `busy.txt` says `replay=lines` or `replay=looks`.
At item 212's rates, each writer, 7 s apart in phase, writes a tool call every 3 s, needs-you 10 s in every 30 and a compact boundary every 60 s, about 0.8 look changes a second.
`perf_test.py` covers each kind of line and the schedule, and `perf_busy_test.py` the flag.

Three deviations, agreed with item 212 and the performance manager:

- **No context climb.** The look key reads `compactions` and `litCourse`, not the percentage, so a compact boundary stands in for it, and no written line carries usage, so context and cost stay where the scenario put them.
- **No resting.** A session record's status wins over its transcript, and resting needs the process gone, which a written line cannot do. So kind 4 is working ↔ needs-you on a busy record (a pending `AskUserQuestion`) and needs-you ↔ waiting on an idle one (a `ScheduleWakeup`).
- **The done check runs after the close.** The performance manager runs the full-zoom LOOKLOG run on `layers` with 6 writers itself. Before landing, a daemon with no city on a staged `layers` home reported, over 70 s, every written session's tool calls, its needs-you or waiting in and out, and one compaction each.

It also found that a transcript inside a symlinked project directory was a target of the plain replay, since `O_NOFOLLOW` guards only the last component; targets must now resolve inside the scratch home's `.claude`, with a test that pins it.
