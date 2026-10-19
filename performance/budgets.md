# Budgets

**Status: proposed on 2026-10-19, not yet Aria's.**
Every number below is a proposal to argue with.
When Aria sets one, mark its row *set*, with the date, and an acceptance test or a release check can gate on it.

The reference is a modest machine: 8 GB of memory, four to eight cores, integrated graphics, on macOS or Linux.
Whoever measures on a bigger machine should measure the same numbers and judge them against these.
Mostly that comes out the same, because the large numbers in the 2026-10-19 report do not depend on the machine's size.

## Daemon

The design already promises this in principle 5 of `botropolis/DESIGN.md`: *a few megabytes, idles on inotify and hook pushes*.

| measure | proposed budget | 0.1.7 | 0.2.2 | status |
| --- | --- | --- | --- | --- |
| CPU, mean over 10 min with sessions working | ≤ 2% of one core | 0.7% | 35.6% | proposed |
| CPU, p95 of 1 s samples | ≤ 25% of one core | 3.5% | 166% | proposed |
| `Private_Dirty`, settled | ≤ 32 MiB | 8 MiB | 18 MiB | proposed |
| garbage collection share of CPU | ≤ 20% | — | ~61% | proposed |

## First launch (cold start)

The first scan and ingest may take as long as they need, but they must not take the machine.

| measure | proposed budget | status |
| --- | --- | --- |
| CPU while the first scan runs | ≤ one core in all, at background priority, whatever `GOMAXPROCS` is | proposed |
| `Private_Dirty` peak during the first scan | ≤ 256 MiB | proposed |
| the city is usable during the first scan | yes: a map with what is known so far, and a percentage for the rest | proposed |
| the first scan survives being interrupted | yes: resumes where it stopped, never starts over | proposed |

## City

| measure | proposed budget | 0.1.7 | 0.2.2 | status |
| --- | --- | --- | --- | --- |
| `Private_Dirty` + GPU memory, window open | ≤ 512 MiB together | see the report | 3.9 GB + 3.0 GB | proposed |
| Go live heap after start-up | ≤ 200 MB | 86–98 MB (Xvfb) | 3,714 MB | proposed |
| `Private_Dirty` slope over 10 minutes | ≤ 1 MiB/min | | | proposed |
| CPU, visible and drawing | ≤ 20% of one core (14.5% on Aria's desk, item 3) | | | proposed |
| CPU, hidden or unfocused | ≤ 1% of one core | | 0.4% | proposed |
| start-up peak (`VmHWM`) | ≤ 1 GB | | 8.5 GB | proposed |

GPU memory counts against the budget because on integrated graphics it is the same RAM.
