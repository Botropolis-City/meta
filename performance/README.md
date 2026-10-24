# Performance

How to measure what Botropolis costs a machine, the tools that do it, and every report taken with them.
It sits in the meta repository because the reports compare releases and machines, and a regression is filed as a roadmap item here.

**The machine that matters is a modest one** (Aria, 2026-10-19): a non-developer's Mac, or a developer's laptop with limited memory, on integrated graphics.
On integrated graphics the city's textures come out of system RAM.
A fast developer workstation is not the reference: if a build is fine there and heavy on a modest laptop, it is heavy.
**First launch must not overwhelm the machine**, even to build a cache that makes later launches fast.
Someone whose laptop stalls the first time will not open the app again, so expensive first-run work has to be throttled, backgrounded, and shown with how far along it is.

| | |
| --- | --- |
| [method.md](method.md) | what to quote and why, the five runs, what the environment changes, and the traps already paid for |
| [budgets.md](budgets.md) | the limits a build must stay inside on a modest machine, and the system requirements they add up to (set 2026-10-19) |
| [templates/report.md](templates/report.md) | the shape of a report |
| [reports/2026-10-19-laptop-igpu-0.2.2.md](reports/2026-10-19-laptop-igpu-0.2.2.md) | 0.2.2 against 0.1.7: the daemon 50× busier, the city 3.7 GB of Go heap and 3 GB of GPU memory |
| [reports/2026-10-19-ultra7-265u-igpu-0.2.2.md](reports/2026-10-19-ultra7-265u-igpu-0.2.2.md) | 0.2.2 and HEAD on a second iGPU laptop: the city ~1.9 GB settled and 3.8 GB at start-up, first launch at 3.6 cores, a probe of 970 MiB; items 156–165 |
| [reports/2026-10-21-ultra7-265u-igpu-r871.md](reports/2026-10-21-ultra7-265u-igpu-r871.md) | r871 after items 191–195: start-up burst gone, settled 0.7–0.8 GB, a real-history frame still 17–48 ms, a hidden city rebuilding on every update |
| [reports/2026-10-22-ultra7-265u-igpu-r905.md](reports/2026-10-22-ultra7-265u-igpu-r905.md) | r905, focused, real history: 400 MiB and 8.7 ms at fit, 620 MiB and 19 ms at full zoom, 61% of a core focused, a hidden city within budget |
| [reports/2026-10-21-ultra7-265u-igpu-item-157.md](reports/2026-10-21-ultra7-265u-igpu-item-157.md) | item 157 against r871: collections 1,104 → 38 a minute settled, first launch 265 → 73 CPU-seconds; settled CPU still 7.6% against 2% |
| [reports/2026-10-22-ultra7-265u-igpu-item-159.md](reports/2026-10-22-ultra7-265u-igpu-item-159.md) | item 159 against r873: the first read held to half a core from 10 s on, 28 → 8 samples over a core, all in the unpaced first load (item 203); a quit re-reads the first load, not the read |
| [reports/2026-10-22-ultra7-265u-igpu-item-162.md](reports/2026-10-22-ultra7-265u-igpu-item-162.md) | item 162 against r871 on the metropolis demo: settled own + GPU 689 → 355 MiB at fit, Go heap 141 → 24 MB, 528 → 250 MiB under Xvfb; the real history and full zoom are owed |
| [reports/2026-10-22-ultra7-265u-igpu-item-196.md](reports/2026-10-22-ultra7-265u-igpu-item-196.md) | item 196 against r873: settled CPU 0.7% mean, 5.4% at p95 on a quiet night (1.2–1.8% loaded, in the acceptance test); reads 1.0 → 0.1 MiB/s |
| [reports/2026-10-24-ultra7-265u-igpu-item-236.md](reports/2026-10-24-ultra7-265u-igpu-item-236.md) | item 236: movers cost 16 of the metropolis's 25 commands by day; one page is four textures to Ebitengine; a level-aware batch key gives 26/43 → 23/40 and item 222 27/44 → 24/41; sprites without mipmaps save 5.2 MiB, none at full zoom |
| [reports/2026-10-24-ultra7-265u-igpu-test-performance-r996.md](reports/2026-10-24-ultra7-265u-igpu-test-performance-r996.md) | the baseline for `make test-performance` at r996: all pass; only item 213's 2,000-session daemon misses its budget, 2.71% of a core against 2% |

## Tools

All in [`tools/`](tools/), each with `--help`.

| tool | what it does |
| --- | --- |
| `perf-env` | the machine, versions, GPU, config and history size, without hostnames or paths |
| `perf-sample` | per-process CPU, `Private_Dirty`, `Pss`, swap, GPU memory, threads, fds and I/O, as CSV |
| `perf-report` | first, last, min, max, mean, p50, p95 and slope per minute of a CSV, plus the Go heap from a gctrace log |
| `perf-daemon-ab` | several daemon builds side by side against the same live `~/.claude`; `--cold` for a first launch |
| `perf-city` | open the city, sample it and the daemon, optionally hide it part-way |
| `perf-busy-city` | a city on a busy desk, made repeatable: the real history linked read-only into a scratch home, demo sessions writing every 200 ms |
| `perf-pprof-build` | build any revision with a pprof endpoint, without touching the checkout |

`make perf-env`, `make perf-daemon` and `make perf-city` run the common cases from the root, and `make perf-busy PERF_BUILD=dir` replays a busy desk under the landing lock.
`make test-unit` runs the tools' own tests.
The `perf-analysis` skill walks a session through a full run and its report.
