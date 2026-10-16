# 94. The power plant undercounts sessions that stopped in the last day

**Open, in progress since 2026-10-16 in the session "item 94". Filed 2026-10-16 (r462), from a finding item 86 reported. Nobody's call — a defect with a known fix.**

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
