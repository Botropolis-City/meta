# 319. A failed soak pre-flight leaves no evidence of why the city's window was not found

**Fixed 2026-10-28 (`ca8ffe3`, r1191 of meta). Filed 2026-10-28 (r1204), from 0.3.3's third soak (server 3101917). Nobody's call — a defect.**

The third soak's set-up passed (item 313's i3 fix held: *i3 started on :0 as soak, and answers i3-msg*), and its pre-flight then failed with *the city's window was not found; see /home/soak/run/preflight*.
The runner's `diagnose` does not collect that directory — the pre-flight's `env.txt`, `perf-city.err` and the city's log — so whether the city never started, crashed, or took longer than `perf-city`'s 30 s to show its window on that iGPU cannot be told.
The soak user's i3 config also lacks `# i3 config file (v4)`, so i3 converts it from v3 at start and logs that as an error.

## The fix

1. `diagnose` collects the pre-flight's output directory, and the soak's `--out`, whatever it is.
2. The i3 config declares v4.
3. If the evidence shows a slow first window, the window wait follows it, as a measured bound rather than a guess.
4. Tests: a failed pre-flight's diagnostics hold its `env.txt` and logs; the i3 config's first line is the v4 header.

The fourth 0.3.3 soak waits on this, so it cannot fail blind in the same place.

## Decided

- **The design and the test tree** (manager, 2026-10-28): approved.
  The 30 s window wait stays, and `perf-city` records `window_found_after_s`, since a bound comes from a measurement, not a guess.
  The pre-flight's failure also says whether the city was running and quotes the end of its log,
  so the runner's own output carries the cause when the diagnostics cannot be collected.

## Fixed

`ca8ffe3` (r1191 of meta):

- The runner's diagnostics collect `/home/soak/run/preflight` and the soak's `--out` whole, as `preflight/` and `out/`.
  Before, they took five fixed files, and their `cp` skipped directories, so naming a directory would have collected nothing either.
  The pre-flight's `--out` and the diagnostics share one constant, `PREFLIGHT`.
- `perf-city` records `window_found_after_s`.
  When no window appears within `PERF_CITY_WINDOW_WAIT` seconds (default 30), it records `city_running_at_window_timeout=yes|no`, stops waiting at once if the city exited, and writes `windows.txt`: each i3 window's `_NET_WM_PID` and i3's tree.
- `perf-soak --preflight`'s failure says whether the city was running and quotes the last ten lines of `city.log`, so the runner's own output carries the cause even when the diagnostics cannot be collected.
- The soak user's i3 config starts with `# i3 config file (v4)`.

Fix 3 is not done, as decided: nothing yet shows a slow first window, so the 30 s wait stays, and the next soak's `window_found_after_s` is the measurement a bound would follow.

Tests: `testing/machines/diagnose_test.py` runs the collection shell against a stand-in box, with and without a pre-flight directory;
`machines_test.py` checks the runner collects the directory it gave the pre-flight and the soak's `out`, and the i3 header;
`perf_soak_test.py` covers a window never found while the city runs, and a stub city that exits at once.
Four mutations were each caught: dropping the pre-flight directory, `cp` without `-r`, dropping the header, and not noticing the city exited.
None of it has run on a real box; the next soak is its first.

For Aria: the first full `make test` here failed 58 tests, because another session's acceptance test had a real city open for 15 minutes, and `perf-city` refuses to start while any windowed city runs.
Rerun after it closed, the suite passed.
That isolation fault is not this item's, and is passed to the roadmap manager.
