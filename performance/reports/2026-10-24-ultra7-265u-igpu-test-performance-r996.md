# The performance tests' first run apart from the landing gate, r996, 2026-10-24

The baseline for `make test-performance`, which [item 226](../../roadmap/226-the-acceptance-suite-takes-sixteen-minutes-to-land.md) took out of `make land` and `make test`, and which the performance manager now runs after each landing that touches drawing, memory or the daemon, and before each release.
Each later run is compared with this one.

**Rig:** Intel Core Ultra 7 265U, 14 threads, 62 GiB; every test on a private Xvfb display or `--headless`, so no GPU drew; Arch Linux, kernel 7.2.
It is the machine of [the item 157 report](2026-10-21-ultra7-265u-igpu-item-157.md).
**Build:** r996 (`8c2b968`, item 226's slice 2), from a detached worktree, built by the target itself.
**History on disk:** none: each test builds its own synthetic or staged home.
**Runs:** `make test-performance` once, 13:30–13:42 MDT, holding `/tmp/botropolis-land.lock` (the target takes it itself), nothing piped; 411 s of tests.
The load average was 10.2 over 1 minute and 15.5 over 5 when it started: the lock keeps landings' gates off the machine, not the item sessions developing beside it.

## Findings

1. **Every test passed**: 10 tests and 70 subtests, exit 0; `TestCalibrateCoreRate` skips by design.
2. **One budget is missed, and it is already filed**: a settled daemon on the 2,000-session home used 2.71% then 2.78% of a core against ≤ 2% (`TestDaemonWithTwoThousandSessions`), which the test skips as unmet for [item 213](../../roadmap/213-the-2000-session-daemon-is-over-its-cpu-budget.md).
3. **Everything else is inside its budget**, with these figures from the tests' own logs:

| measure | budget | r996 | logged by |
| --- | --- | --- | --- |
| settled daemon, synthetic home, sessions writing | ≤ 2% of a core | 1.08%, then 1.31% | `daemon_cost_test.go` |
| settled daemon, 2,000 sessions | ≤ 2% of a core | 2.71%, then 2.78% (unmet, item 213) | `group_cost_test.go` |
| daemon memory, 2,000 sessions | the test's own | 55 MiB `Private_Dirty`, 8 MiB under it | `group_cost_test.go` |
| first launch, 256 MiB of history | ≤ 1 core, ≤ 256 MiB | peak 59% of a core, 28 MiB | `firstlaunch_test.go` |
| first launch, until idle | ≤ 1 core | 32 s, peak 63% of a core | `firstlaunch_test.go` |
| first city frame | | after 0.08 CPU-seconds | `firstlaunch_test.go` |
| city hidden | ≤ 1% of a core | 0.44% | `hidden_cost_test.go` |
| city unfocused and visible | ≤ 1% of a core | 0.96%, and 0.70% over a real-sized statistics store | `hidden_cost_test.go` |
| city settled, headless | | 197 MiB `Private_Dirty`, 27 MB live heap | `memory_test.go` |

The unfocused city's 0.96% is the figure nearest its budget, so it is the first to watch in later runs.

## Later runs

Each run after a landing that touches drawing, memory or the daemon, against this baseline.
The figures are the table's above, in its order of rows, from the tests' own logs.

| run | range | result | daemon settled | 2,000 sessions | first launch peak | first city | hidden / unfocused | city settled | load at start |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r996 (baseline) | | 70 pass, 2 skip | 1.08%, 1.31% | 2.71%, 2.78% | 59%, 28 MiB | 0.08 CPU-s | 0.44%, 0.96%, 0.70% | 197 MiB | 10.2 |
| r998 `241e1a9` | `8c2b968..241e1a9`, item 236 slice 1 | 70 pass, 2 skip | 1.01%, 1.28% | 2.73%, 2.69% | 53%, 30 MiB | 0.12 CPU-s | 0.44%, 0.94%, 0.71% | 194 MiB | 23.1 |
| r1000 `0601797` | `241e1a9..0601797`, item 222 | 70 pass, 2 skip | 1.01%, 1.28% | 2.82%, 3.08% | 57%, 28 MiB | 0.06 CPU-s | 0.44%, 0.92%, 0.69% | 196 MiB | 23.1 |
| r1000 `0601797`, repeated | the same | 70 pass, 2 skip | 1.10%, 1.32% | 2.81%, 2.90% | 54%, 26 MiB | 0.10 CPU-s | 0.50%, 0.96%, 0.70% | 198 MiB | 7.0 |
| r1017 `73d7d69` | `0601797..73d7d69`: items 239, 240, 242, 243, 236 slice 2, 226's settled daemon on 15 s windows | 70 pass, 2 skip | 0.99%, 1.03% | 2.79%, 2.96% | 55%, 26 MiB | 0.10 CPU-s | 0.44%, 0.90%, 0.70% | 201 MiB | 58.0 |

At r1000 the 2,000-session daemon read about 0.1 of a core higher, twice, and is recorded as the machine's load rather than filed: `botropolisd` links neither `pkg/city` nor `pkg/render`, the only code the range changed; its CPU ticks held at 2.16–2.39% in all four runs; and the test itself says this measure spans 2.3–2.6% on a quiet machine.
It is still over its budget, which is [item 213](../../roadmap/213-the-2000-session-daemon-is-over-its-cpu-budget.md).
A single performance test could not be rerun on its own: `make test-acceptance-locked` selects outside the performance tier and ran no tests, so the repeat is the whole suite; item 226 is adding a `RUN` pattern to `make test-performance`.

## What it does not show

- **A GPU.** The city's GPU memory, and so its 512 MiB budget, is only measured on the real display; [item 162](../../roadmap/162-the-city-holds-gigabytes-of-gpu-memory.md)'s runs are where it stands.
- **A quiet machine.** The lock kept landings off, but item sessions were working; a CPU figure here is an upper bound on a quiet machine's.
- **Repeatability.** One run; the next ones will show how far each figure moves between runs on this desk.

## Reproduce

```sh
git -C botropolis worktree add --detach .claude/worktrees/perf-baseline 8c2b968
make -C botropolis/.claude/worktrees/perf-baseline test-performance
```
