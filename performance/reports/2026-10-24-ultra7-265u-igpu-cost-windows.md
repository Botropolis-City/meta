# Two cost tests on 15-second windows, for items 226 and 244, 2026-10-24

Whether two of the daemon's CPU tests read as reliably on two 15-second windows as on two of 30, by the rule [item 226](../../roadmap/226-the-acceptance-suite-takes-sixteen-minutes-to-land.md) and the roadmap manager set: five pairs, 15 s and 30 s interleaved, each started on a quiet machine.

**Rig:** Intel Core Ultra 7 265U, 14 threads, 62 GiB; the daemon on a synthetic home, no GPU involved; Arch Linux, kernel 7.2.
It is the machine of [the item 157 report](2026-10-21-ultra7-265u-igpu-item-157.md).
**Builds:** item 226's candidates, each against its parent: `ecedf05` (the settled daemon at 15 s) against `b23ee33` (r1004, 30 s), and `352dae1` (2,000 sessions at 15 s) against `ecedf05` (30 s), each from a detached worktree at its exact commit.
**Runs:** `make test-performance RUN='^Test…$'` per run, which takes the landing lock itself, alternating 15 s and 30 s for five pairs; each run waited for load under 3 over one minute and under 4 over five, recorded at its start.
**Measure:** what each test gates on, the quieter of its two windows, counted in instructions (item 209).

## Findings

1. **The settled daemon takes 15-second windows**: every run passed, and the worst 15 s share, 1.08%, sits further below the 2% budget than the worst at 30 s, 1.19%; it landed as item 226's `09fb882`.
2. **The 2,000-session daemon keeps 30-second windows**: every run read over 2% and skipped as unmet ([item 213](../../roadmap/213-the-2000-session-daemon-is-over-its-cpu-budget.md)), but the 15 s median, 2.69%, falls below the 30 s range and its worst, 2.84%, above it, so it fails [item 244](../../roadmap/244-the-two-thousand-session-test-may-take-15-second-windows.md)'s rule.
   At 15 s it reads about 0.1 of a core lower in the middle and spreads over 0.32 against 0.09, which could make an item 213 fix look bigger than it is.
3. **A loaded machine could not run this**: from 15:00 to 18:00 the load stayed near 20 and runs waited an hour each for quiet; one pair that ran anyway, at load 16–23, is left out.

## The settled daemon

| pair | 15 s, gated | 30 s, gated | load at start, 15 s / 30 s |
| --- | --- | --- | --- |
| 1 | 0.88% | 1.01% | 1.9 / 2.6 |
| 2 | 1.03% | 1.13% | 2.1 / 1.7 |
| 3 | 1.08% | 1.01% | 2.4 / 2.3 |
| 4 | 0.99% | 1.09% | 2.6 / 2.0 |
| 5 | 1.06% | 1.19% | 2.7 / 2.8 |
| worst | 1.08%, 0.92 under 2% | 1.19%, 0.81 under | |

## The 2,000-session daemon

| pair | 15 s, gated | 30 s, gated | load at start, 15 s / 30 s |
| --- | --- | --- | --- |
| 1 | 2.69% | 2.82% | 0.6 / 0.7 |
| 2 | 2.65% | 2.79% | 0.4 / 0.6 |
| 3 | 2.84% | 2.73% | 0.8 / 1.7 |
| 4 | 2.52% | 2.73% | 2.6 / 2.4 |
| 5 | 2.73% | 2.81% | 1.7 / 1.0 |
| median | 2.69% | 2.79% | |
| range | 2.52–2.84% | 2.73–2.82% | |

## What it does not show

- **Another desk.** Five pairs on one laptop; the spread at 15 s is the finding, and a slower machine would likely widen it.
- **The busy case.** Every counted run was quiet by the rule; how either window reads under load was not compared.

## Reproduce

```sh
make -C <worktree at the candidate> test-performance RUN='^TestDaemonWithTwoThousandSessions$'
make -C <worktree at its parent> test-performance RUN='^TestDaemonWithTwoThousandSessions$'
```

Alternate the two five times, each from load under 3 over one minute and under 4 over five.
