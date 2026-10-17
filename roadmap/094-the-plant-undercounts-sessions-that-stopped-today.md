# 94. The power plant undercounts sessions that stopped in the last day

**Fixed 2026-10-17 (`5d3fe10`, r553). Filed 2026-10-16 (r462), from a finding item 86 reported. Nobody's call — a defect with a known fix.**

Depends on: nothing
Landed: slice 1 (`07967d4`, r545).
Landed: slice 2 (`5d3fe10`, r553).

The plant's 24-hour figures — fresh and cached tokens, the per-model sums and the cost — count only part of any large session that stopped within the last day.

## Where it comes from

A stopped session's transcript is read through a 64 KB head-and-tail window: `stoppedWindowBytes` and `claude.ReadTranscriptWindow` in `botropolis/pkg/state/loader.go`, in the loop over stopped transcripts.
Those windowed transcripts then go into `PowerSince` (`pkg/state/state.go`) beside the live ones, through `snapshot.Power = PowerSince(…src.Stopped…)` at the end of the load.
`PowerSince` sums each transcript's `Hourly` usage for the hours inside the window, and adds each model's `Cost.Models` usage to `ByModel` — and for a windowed read, both hold only what the head and the tail contained.
A session that worked for a few hours yesterday and wrote several megabytes keeps far more than 64 KB of its last day in the middle, so most of its tokens never reach the plant.
Live sessions are read whole and are not affected.

Item 86 found it while marking windowed counts as partial in `status --json` (`usage.partial`), which says the JSON's numbers are partial but does nothing for the plant.

## The fix

Read whole any stopped transcript whose last activity falls inside `PowerWindow`, and keep the window for the rest.
That set is bounded by a day of work, it changes as sessions age out, and the loader's stat-keyed cache means each is read whole once.
The cost the window was there to avoid is a long history of old sessions, which this leaves windowed.

Tests: a stopped transcript larger than the window, active within the last day, should give the plant the same hourly sum as a whole read; one whose last activity is older should still be read through the window.
Item 91's measures include start-up cost, so re-run them and record the difference.

## Answered while building

- **What decides a whole read** (manager, 2026-10-16): the transcript's own last activity, from the window's tail, inside `PowerWindow` of the load's `now` — not the file's modification time, so it agrees with `PowerSince`'s own filter and a touched or copied file changes nothing.
- **The test tree** (manager, 2026-10-16): approved as proposed in `pkg/state/loader_test.go` — a whole read's plant figures and no partial mark when recent, a second load reading nothing, and the window and a partial mark when older — with `now` injected and reads counted through a seam.
- **Item 91's measures** (manager, 2026-10-16): re-run and the difference recorded here; a gate that goes red is not loosened, and comes back to Aria.
- **The +3.4 s cold start** (Aria, 2026-10-17): add a second slice, then close — read only the part of a recent transcript inside the power window, its head for the title and its tail backwards until the timestamps fall before the window opens, with the plant's figures equal to a whole read's.
- **Slice 2's bound** (manager, 2026-10-17, from Aria's "equal to a whole read"): the walk back stops at the start of the power window's first hour, includes the first line of any message it has seen, and goes on until it finds a cost-state record, so a resumed session's cost and per-model figures stay a whole read's; a file without one is read to its start. Its tree was approved.

## What it cost

The loader decides on the window's own last timestamp, not the file's mtime, so it agrees with `PowerSince`'s own filter (the manager's call, 2026-10-16).

Item 91's benchmarks don't reach this path.
Their fixtures are three-line transcripts, below the window, so they read the same before and after.
Their gates stayed green.
The wall times moved — `StartASessionAnywhere/1000` went from 2.3 s to 3.8 s — but the load average was 25–31 from other sessions' builds, and an unchanged path can't account for the difference.

So it was measured on the real home instead: 44 transcripts, 21 of them active in the last day, 1.0 GB in all.
Three cold loads each, before and after, interleaved:

| | before | after |
| --- | --- | --- |
| plant, fresh tokens over 24 hours | 6.4 M | 17.9 M |
| plant, cached tokens over 24 hours | 251 M | 1,488 M |
| transcript reads | 48 | 63 |
| allocated | 56 MB | 142 MB |
| cold load | 1.15–1.32 s | 4.5–6.2 s |
| warm load | 5–98 ms | 5–16 ms |

The plant had been showing about a third of the fresh tokens and a sixth of the cached ones.
A cold start costs about 3.4 s more on this home, and a warm load costs no more, because the stat-keyed cache reads each transcript once.

## Slice 2: from the window on

Aria's ruling, 2026-10-17: rather than accept the 3.4 s, read only what the plant sums, then close.
`claude.ReadTranscriptSince` reads the head window for the title, then walks back from the end to the start of the hour the plant's window opens in, which is where `PowerSince`'s buckets begin.
Two rules keep the figures equal to a whole read's (the manager's calls, 2026-10-17):

- a message whose lines straddle that hour is read from its first line, because a whole read dedups by message id and buckets the message there;
- the walk goes on until it meets a cost-state record, because the cost and `ByModel` are the last one's.
  Past the hour that search is a byte match, not a decode, since those hours are not the plant's.

A transcript whose head began inside the hour is read whole with no walk, and so is one whose walk reaches the head.

The real home on 2026-10-17: 47 sessions, four cold loads of each build, interleaved, load average 5–9:

| | before item 94 | slice 1 | slice 2 |
| --- | --- | --- | --- |
| plant, fresh tokens over 24 hours | 3.3 M | 4.6 M | 4.6 M |
| plant, cached tokens over 24 hours | 136 M | 340 M | 340 M |
| transcript reads | 52 | 59 | 59 |
| allocated | 61 MB | 98 MB | 180 MB |
| cold load | 0.97–1.38 s | 2.47–2.97 s | 1.96–2.52 s |

Slice 2's figures are identical to slice 1's, which read whole, and its cold load is about 0.5 s shorter.
Where the walk applies, it pays: a 67 MB transcript that began before the window read in 35 ms instead of 162 ms, and an 89 MB one in 162 ms instead of 283 ms.
Most of what remains is inherent to the fix.
On this home most of the day's transcripts began inside the day, so they are read whole either way.
Allocation is higher than slice 1's because the walk decodes each line of the region once and the forward read decodes it again.

A transcript with no cost-state record is walked to its head and then read whole, which is slice 1's cost for it plus the walk.
Of the 14 transcripts active in the last day, 9 have no cost-state record, live sessions included; if that count grows among stopped ones, it is where the time goes.

## Closed

Fixed in two slices: slice 1 read whole each stopped transcript active in the last day (`07967d4`, r545), and slice 2 reads it from the plant's window on (`5d3fe10`, r553).
`TestStoppedTranscriptsInThePowerWindow` in `pkg/state/loader_test.go` holds the plant to a whole read's figures, and `TestReadTranscriptSince` in `pkg/claude/since_test.go` covers the straddling hour, a message split across it, an old cost-state record, a file wholly inside the window, and how many bytes each read takes.
Every rule in the walk was mutated red before it was trusted.
The CHANGELOG entry is under `[Unreleased]`, *Fixed*.
One deviation, for Aria: a cold start still costs about 1 s more than before item 94 on this home, because most of the day's transcripts began inside the day and have to be read whole.

