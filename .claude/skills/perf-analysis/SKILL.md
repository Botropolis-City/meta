---
name: perf-analysis
description: >-
  Measure what Botropolis costs on this machine — the daemon's CPU, I/O and
  memory, and the city's CPU, memory, GPU memory and Go heap — repeatably,
  and write the result as a report in performance/reports/. Use when asked
  to profile, benchmark, measure resource usage, find a leak or a CPU
  regression, compare two builds or releases, or check that a performance
  fix worked.
---

# Performance analysis

Run it from the meta repository's root, `~/workspaces/github/Botropolis-City`.
The method, and why each number is the one quoted, is `performance/method.md`; read it first.
Earlier reports are in `performance/reports/` and are the baseline to compare against.

## 1. Write down the desk

```sh
performance/tools/perf-env
```

Keep its output beside the run.
Every number is a measurement of one desk, and this is the desk.

## 2. Daemon at rest

Close any open city first (`pgrep -a -x botropolis | grep ' city'` finds one).

```sh
out=~/.local/state/botropolis-perf/daemon-$(date +%Y%m%d-%H%M%S); mkdir -p "$out"
performance/tools/perf-sample --name botropolisd --interval 1 --duration 600 --out "$out/samples.csv"
performance/tools/perf-report "$out/samples.csv"
```

Read `cpu_pct` mean and p95, `read_mib_s` and `private_dirty_mib`'s slope.
A daemon that "idles on inotify" (DESIGN.md, principle 5) should be near zero CPU and I/O between bursts.

## 3. Daemon A/B, when a regression is suspected

Build each version from `git archive`, never by checking out a tag in the live tree:

```sh
for t in vA vB; do
  mkdir -p /tmp/perf-$t && git -C botropolis archive $t | tar -x -C /tmp/perf-$t
  (cd /tmp/perf-$t && go build -o botropolisd ./cmd/botropolisd && go build -o botropolis ./cmd/botropolis)
done
performance/tools/perf-daemon-ab --seconds 300 vA=/tmp/perf-vA/botropolisd vB=/tmp/perf-vB/botropolisd
```

To bisect, swap the tags for commits and repeat on the halves; the side-by-side run is fair at any afternoon's load.

## 4. City

This opens a window on the real display, so **ask Aria first** unless she has said the GUI is yours for this run.
`--headless` never pops anything up, but its llvmpipe numbers are only good for comparing two builds.

```sh
performance/tools/perf-city --seconds 900 --hide-after 600
```

Reject the run if `frames drawn` in its `report.md` is zero, unless the run was meant to measure a hidden window.
Read `private_dirty_mib`, `gpu_mib`, the Go heap table, and each one's slope.
GPU memory on an integrated GPU is system RAM that appears in no other column.

## 4b. A busy desk, when "sessions working" matters

A budget measured "with sessions working" cannot wait for real sessions to happen to write: a quiet evening and a busy afternoon differ by more than most fixes do.
Replay them (method.md, run 6), one build after another:

```sh
performance/tools/perf-pprof-build REV /tmp/perf-REV
make perf-busy PERF_BUILD=/tmp/perf-REV
```

It links the real history into a scratch home read only and makes two demo sessions write a line every 200 ms; nothing under `~/.claude` is copied or written.
Read the run's `busy.txt` before quoting anything: it says whether the focus was handed back, whether the monitor was on and whether the CPU profile was taken, and a skipped step there changes what the run measured.

## 5. Write the report

Copy `performance/templates/report.md` to `performance/reports/YYYY-MM-DD-<rig>-<what>.md`, fill it in from the runs' `report.md` files, and link it from `performance/README.md`.

- Name the rig by its hardware, never its hostname.
- Quote counts and sizes, never a project path, a session title or a spend.
- Never name the day job; see the meta CLAUDE.md.

Then `make docs-check test`, and commit only the paths you name: `git commit -- performance/ ...`.
If a finding is a defect, file it with `roadmap-add` and cite the report from the item.
