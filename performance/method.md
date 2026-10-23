# How to measure Botropolis

This is the method behind every report in [`reports/`](reports/).
It carries over what [`botropolis/design/what-it-costs.md`](../botropolis/design/what-it-costs.md) already paid for,
and adds what the 2026-10-19 analysis found.
Read the rules in botropolis's `rules/` before quoting any number, especially
[a-plausible-wrong-number.md](../botropolis/rules/a-plausible-wrong-number.md) and
[a-number-can-be-right-and-mean-nothing.md](../botropolis/rules/a-number-can-be-right-and-mean-nothing.md).

## What to quote

| quantity | where it comes from | quote it? |
| --- | --- | --- |
| CPU | `utime+stime` from `/proc/<pid>/stat` over an interval, as % of one core | yes, with the sample length and the frames drawn |
| own memory | `Private_Dirty` from `/proc/<pid>/smaps_rollup` | **yes: this is the process's own memory** |
| fair share | `Pss`, same file | when a shared page genuinely is a cost |
| swap | `Swap`, same file | yes, because memory pressure hides growth here |
| GPU memory | `drm-total-*` in `/proc/<pid>/fdinfo/<fd>` for each `/dev/dri` fd | yes; **on an integrated GPU it is system RAM and is not in any of the above** |
| Go heap | `GODEBUG=gctrace=1` on stderr: `A->B->C MB`, where C is the live heap | yes, to split Go memory from driver memory |
| I/O | `rchar` and `wchar` from `/proc/<pid>/io`, as a rate | yes for the daemon: re-reading transcripts shows up here first |
| `VmRSS` | `/proc/<pid>/status` | **no**: it counts shared libraries (68% of a client's figure, item 61) |
| cgroup `memory.peak` | systemd's `MemoryPeak=` | **no** on its own: it includes page cache from reading transcripts, so the daemon read 541 MB against a 36 MB high-water mark |

`performance/tools/perf-sample` records all of the quotable rows every interval, per process, as CSV.
`performance/tools/perf-report` turns that CSV into first, last, min, max, mean, p50, p95 and a least-squares slope per minute.
**The slope is the leak signal.**
A short run's slope is mostly start-up, so drop it with `--since`, and only call something a leak when its slope holds over a long run.

## The four runs

Each run writes a directory holding `env.txt` (from `perf-env`), the CSVs, the logs and a `report.md`.
The default location is `~/.local/state/botropolis-perf/`, outside every repository, because a run's raw logs are not reviewed for publishing.
Only the numbers go into a report here.

1. **Daemon at rest:** `perf-sample --name botropolisd --interval 1 --duration 600`, with no city open.
   This is the cost of having Botropolis installed at all.
2. **Daemon A/B:** `perf-daemon-ab OLD=path/to/botropolisd NEW=path/to/botropolisd`.
   It runs both builds at once against the same live `~/.claude`, so both see the same session activity.
   Two daemons measured at different times measure two different afternoons.
   Each gets a copy of the state directory and config, its own socket, and a stub `claude` on its `PATH`, so neither spawns a usage probe or a summary.
3. **City, visible then hidden:** `perf-city --seconds 900 --hide-after 600`.
   The city opens on the real display under `GODEBUG=gctrace=1 BOTROPOLIS_FRAMETIME=1`.
   After `--hide-after` seconds it moves to i3's scratchpad, so the last part measures a hidden window.
   **A run that drew zero frames is not a measurement**, and the report prints the frame count first for that reason.
4. **City A/B:** run `perf-city --bin` once per build, one after the other, with nothing else changed.
   Only the city can't be run side by side, because two windows compete for focus and for the GPU.

5. **Cold start:** the daemon with an empty state directory, as on a new user's first launch.
   `perf-daemon-ab --cold LABEL=BINARY` runs it, until its CPU has been idle for a minute or `--seconds` runs out.
   Report how long until idle, the peak CPU and `Private_Dirty`, and the I/O total.
   **This is the run that decides whether someone opens the app a second time.**

6. **A busy desk, replayed:** "sessions working" made controlled and repeatable, rather than waiting for real sessions to happen to write.
   A quiet evening and a busy afternoon differ by more than most fixes do (2026-10-22: 0.9% of a core quiet, 2.7% busy, for the same build).
   `perf-busy-city BUILD_DIR`, or `make perf-busy PERF_BUILD=BUILD_DIR`, stages a demo scenario into a fresh scratch home and links every transcript, session record and `history.jsonl` under `~/.claude` into it **read only, by symlink**: nothing of `~/.claude` is copied, and the replay refuses to write through a link.
   A daemon of the build runs with `HOME` set to that home and every XDG directory inside the run's scratch tree, so it opens a statistics store as production does and nothing of the real state, config, cache or data is touched.
   Once the daemon's CPU has been idle for 20 s (at most 600 s), the city opens on the real display, and from 25 s two of the demo's own live sessions each write a user line every 200 ms, as the daemon-cost acceptance tests do.
   It samples 480 s and, for a build made by `perf-pprof-build`, profiles the city's CPU for 300 s from 120 s.
   Where `i3-msg` and `xprop` exist, the city takes the focus for 20 s and gives it back, so the rest measures a visible, unfocused city; elsewhere that step is skipped, and the run's `busy.txt` says so, as it says whether the monitor was on, since a locked screen keeps the focus from every window.
   Runs before 2026-10-23 gave the daemon `--home` instead, and a daemon pointed at a home opens no statistics store (item 165), so their daemon figures are not production's.
   Run it under the landing lock, one build after another; `make perf-busy` takes the lock itself.

Raw runs and profiles go under `~/.local/state/botropolis-perf/` from the start, never only in a session's scratch directory: a profile kept nowhere else was lost with its scratch on 2026-10-22 and had to be taken again.

To find *where* the time or memory goes, build with a pprof endpoint (`perf-pprof-build REV`), then take `go tool pprof -top` of `/debug/pprof/heap` or `/debug/pprof/profile?seconds=60`.

To build an older release without touching a checkout:

```sh
mkdir -p /tmp/v0.1.7 && git -C botropolis archive v0.1.7 | tar -x -C /tmp/v0.1.7
(cd /tmp/v0.1.7 && go build -o botropolisd ./cmd/botropolisd && go build -o botropolis ./cmd/botropolis)
```

## What the environment changes

Every number is a measurement of one desk, so `env.txt` goes beside it.
These are the inputs that have moved numbers by more than the change being measured:

- **Which GPU draws.** Mesa on an integrated GPU, NVIDIA's driver, and llvmpipe under Xvfb give different memory by a factor of four (357 MB against 1.35 GB on one machine).
  On an iGPU, texture memory comes out of system RAM.
  So **`--headless` is fine for comparing two builds and useless for an absolute figure.**
- **How much history is on disk.** The daemon catalogues every stopped transcript it has ever seen.
  `env.txt` records the transcript count and size for that reason.
- **How busy the machine's sessions are.** The daemon works on file events.
  An afternoon with twenty item sessions writing is a different load from a quiet evening, and that is why the A/B runs builds side by side.
- **Focus.** An unfocused or hidden window draws nothing by design, so its cost is the hidden cost, whatever the label says.

## Traps already paid for

- **A waiter must never match a string its own command line contains.**
  `pkill -f perf-daemon-ab` killed the shell that ran it, and the run with it, on the day this folder was written.
  Use `pgrep -x`, a pid, or `wait`.
  The same day, a waiter's `pgrep -f` pattern matched its own command line too and could never exit.
- **Never edit a script while it runs.**
  Bash reads a script as it goes, so an edit mid-run makes it execute from a shifted offset: `perf-daemon-ab` died on `cho: command not found` after its runs had finished, and wrote half a report.
- **Name-matching samples every process of that name.**
  `--name botropolisd` caught the A/B daemons alongside the real one; pass `--by-pid` to `perf-report`, or sample `--pid`.
- **The city is single-instance.**
  Starting a second one raises the first window and exits; give the second its own `XDG_RUNTIME_DIR` and `--socket` the real daemon (see `perf-pprof-build --help`).
- **`VmRSS` and cgroup peaks are the wrong numbers**; see the table above.
- **The instrument must not be inside the thing it measures.**
  Sample from outside the process.
  `perf-sample` reads `/proc`, and the only thing it adds to the app is `GODEBUG`, which changes no code path.
- **A cached Go test is a test that did not run**, so pass `-count=1` to anything benchmarked.

## Keeping the record

A report is [`templates/report.md`](templates/report.md) filled in, saved as `reports/YYYY-MM-DD-<rig>-<what>.md`, and linked from [README.md](README.md).
Name the rig by its hardware, never by its hostname: this repository is public, and a hostname can name an employer.
Quote counts and sizes only, never a project path or a session title.
