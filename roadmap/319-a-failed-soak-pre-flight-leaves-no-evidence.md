# 319. A failed soak pre-flight leaves no evidence of why the city's window was not found

**Open. Filed 2026-10-28 (r1204), from 0.3.3's third soak (server 3101917). Nobody's call — a defect.**

The third soak's set-up passed (item 313's i3 fix held: *i3 started on :0 as soak, and answers i3-msg*), and its pre-flight then failed with *the city's window was not found; see /home/soak/run/preflight*.
The runner's `diagnose` does not collect that directory — the pre-flight's `env.txt`, `perf-city.err` and the city's log — so whether the city never started, crashed, or took longer than `perf-city`'s 30 s to show its window on that iGPU cannot be told.
The soak user's i3 config also lacks `# i3 config file (v4)`, so i3 converts it from v3 at start and logs that as an error.

## The fix

1. `diagnose` collects the pre-flight's output directory, and the soak's `--out`, whatever it is.
2. The i3 config declares v4.
3. If the evidence shows a slow first window, the window wait follows it, as a measured bound rather than a guess.
4. Tests: a failed pre-flight's diagnostics hold its `env.txt` and logs; the i3 config's first line is the v4 header.

The fourth 0.3.3 soak waits on this, so it cannot fail blind in the same place.
