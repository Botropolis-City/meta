# Budgets

**Set by Aria on 2026-10-19**, from proposals argued one at a time.
A budget is a limit a build must stay inside on the reference machine, and a release that breaks one is a defect to file, not a number to note.
Each row says how it is measured; [method.md](method.md) has the runs, and the figures for 0.1.7 and 0.2.2 come from [the 2026-10-19 report](reports/2026-10-19-laptop-igpu-0.2.2.md).

The reference is a modest machine: the minimum in the system requirements below, on integrated graphics, where GPU memory is system RAM and counts against every memory budget.
A bigger machine does not change a budget.
Measure the same numbers there and judge them against these.

## System requirements

What the budgets add up to, for Botropolis's own footprint.
The Claude Code sessions a user runs come on top, at about 140–200 MiB each (measured 2026-10-19), and are the user's choice, not the app's.

| | Minimum | Recommended |
| --- | --- | --- |
| Memory | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Graphics | integrated, OpenGL 3.3 on Linux, Metal on macOS | any |
| Disk | SSD | SSD |
| Botropolis's share | ~0.55 GB steady (~7%), ≤ 1.55 GB at the worst moment | the same, ~3.5% steady |

Aria, 2026-10-19: reasonable for a cheap development machine, and bigger than she had hoped.
On an 8 GB machine the steady state fits beside a normal day; **the start-up peak is what would push it into swap**, so the first-launch rules below exist to keep the city's peak, the first scan and any helper from ever landing together.

## Daemon

The design promises this in principle 5 of `botropolis/DESIGN.md`: a few megabytes, idling on inotify and hook pushes.

| measure | budget | how it is measured | 0.1.7 | 0.2.2 |
| --- | --- | --- | --- | --- |
| CPU, mean | ≤ 2% of one core | 10 minutes with sessions working, `perf-daemon-ab` | 0.2–0.7% | 6–36% |
| CPU, bursts | ≤ 25% of one core at p95 | 1-second samples, same run | 2–3.5% | 45–166% |
| memory, settled | ≤ 64 MiB `Private_Dirty` | same run; spent on caches that save CPU, not on a tight heap | 8 MiB | 18 MiB |
| disk reads, mean | ≤ 1 MiB/s, and nothing already ingested is read again | `read_mib_s`, same run | 0.3–1.1 | 0.7–7 |
| disk reads, spikes | ≤ 25 MiB/s over any 5-second window, outside first launch | `read_kib_s` at 1 s, rolling 5 s | 53 once | 128–266 |

## First launch

The first scan may take as long as it needs; it may not take the machine, and it may not cost the first impression.

| measure | budget | how it is measured |
| --- | --- | --- |
| CPU | ≤ 1 core in all, at background priority, whatever `GOMAXPROCS` is | `perf-daemon-ab --cold`; 0.2.2 used up to 4 cores |
| memory | ≤ 256 MiB `Private_Dirty` at any point, however large the history | same run |
| a map | within 5 s of opening the city, with what is known so far and a percentage for the rest | by eye and the frame log |
| any wait before the first frame | a loading bar showing real progress, never a blank or frozen window (Aria, 2026-10-19) | by eye |
| the city's CPU before its first frame | ≤ 2.5 CPU-seconds of the city's own process from start to its first frame, on the 600-district fixture, headless, a `--record` or `--screenshot` run included, within `firstMapLimit` (Aria, 2026-10-28, item 315) | [item 311](../roadmap/311-a-recording-city-never-opens-on-six-hundred-districts.md)'s test, the city's `/proc` CPU ticks at start and at the first file |
| interruption | quitting part-way loses nothing; the next launch resumes where it stopped | quit during `--cold`, relaunch, compare read totals |

**The first frame's CPU is 2.5 CPU-seconds** (Aria, 2026-10-28, item 315): it is a cost paid once, on a stress city whose map is already inside the 5-second bar, and 2.5 holds what opening costs now, 1.6–2.1 headless, while catching a slide back to the 3–4 it cost before item 315.
It was 1 CPU-second from 2026-10-27, an estimate of what opening ought to cost (item 311): building the scene, about 0.3, one fitted frame under llvmpipe, priced at 0.3–0.5, and a paced wait.
The frame was the part that was wrong: a first frame bakes every look cold, and item 315 measured it at about 1.2 CPU-seconds (Go about 0.5, GL calls 0.35, rasterising 0.45), so the opening came to 1.47 even windowed on this machine's GPU.
Item 315 took it from 3–4 CPU-seconds to 1.6–2.1 first: a garbage collector spiralling against the city's 300 MiB limit, an opening panel drawn where nobody could see it, and a quadratic street search.
A whole core for the five seconds of `firstMapLimit` would still pass a city that spins one core the whole time it waits, which is why the bar is not five.

## City

| measure | budget | how it is measured | 0.1.7 | 0.2.2 |
| --- | --- | --- | --- | --- |
| memory, settled, window open | ≤ 512 MiB `Private_Dirty` + GPU together | `perf-city` | ~1.15 GB | 4.5–7 GB |
| memory, start-up peak | ≤ 1 GB `Private_Dirty` + GPU at any moment | `perf-city` at 1 s through the first 10 s | ~2.2 GB | 8–11 GB |
| CPU, visible and drawing | ≤ 10% of one core mean, ≤ 10 ms of CPU a frame | `perf-city` with frames drawn, `BOTROPOLIS_FRAMETIME` | 21.6 ms | 41 ms |
| hidden or unfocused | ≤ 1% of one core, and own memory ≤ 256 MiB within 30 s of hiding | `perf-city --hide-after` | — | 0.4%, 4 GB kept |
| growth | ≤ 1 MiB an hour of `Private_Dirty` + GPU | an 8-hour soak with sessions working, before each release: `perf-soak`, per phase, visible and hidden | not measured | not measured |

## Background helpers

The usage probe, summaries, and anything else that runs Claude Code on the app's behalf.

| measure | budget |
| --- | --- |
| memory | ≤ 300 MiB peak across the helper's whole process tree |
| duty cycle | runs for at most 10% of its interval (≤ 30 s of a 5-minute refresh), and its result arrives well inside the interval, so updates never feel sporadic |
| how | from deltas and cached data rather than from scratch; a longer, leaner run is acceptable only when it is truly in the background and keeps the duty cycle |
| isolation | never starts the user's MCP servers; never more than one helper at a time |

Aria, 2026-10-19, on helpers: reasonable depending on how often it happens — "if it were to take 2 minutes to update every 5 minutes, that feels bad. We should try to make this quicker and less memory using deltas and cached data."
0.2.2's usage probe peaks at ~806 MiB across seven processes, every refresh.
