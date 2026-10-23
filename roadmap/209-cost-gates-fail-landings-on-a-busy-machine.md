# 209. Cost gates fail landings at random while the machine is busy

**Open, in progress since 2026-10-22 in the session "item 209". Filed 2026-10-22 (r921), from item 203's landing. Nobody's call — a defect in the gates; every landing runs them.**

Depends on: nothing
Landed: slice 3 (`08f1e73`, r925).
Landed: slice 4 (`b4304c0`, r934).

Item 203's changelog-only landing failed on three gates that measure cost, none of which its change touches, and a rerun alone at a load of 15–19 failed again:

- **`TestAnUnwatchedCityUnderAStreamOfSnapshots`** ([item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md)): hidden 1.19% against 1%, then unfocused **3.4% against 1%**. The unfocused case gates the city's own counted decoding and layout time, which is **wall-clock** inside the process, so machine load moves it directly.
- **`TestGroupingCostPerPrompt`** ([item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md)): 52.8 ms against 50.
- **`TestScriptsAreInTheCacheKey`**: "not cached", a flake of its own.

A gate that a busy machine fails is not measuring the code, and it fails other items' landings at random — the cost every session pays while several build at once.

## The fix

Measure CPU, not wall time, wherever a gate means CPU: the decoding and layout counter reads the thread's CPU time (`RUSAGE_THREAD`, or `CLOCK_THREAD_CPUTIME_ID` on a locked thread) rather than elapsed time; per-prompt grouping cost the same. Where a gate must read process CPU, take the quieter of two windows, as [item 196](196-a-settled-daemon-bursts-to-several-cores-on-rescans.md) did. Look at `TestScriptsAreInTheCacheKey`'s "not cached" separately.
The limits stay as they are (gate on targets); only what is measured changes.

Tests: each gate passes its own red-check (the pre-fix code still fails it) and passes at a load of ~30 on this machine (run beside a `make test` of another worktree), five runs in a row.

## What working it found (2026-10-22)

**CPU time is not load-independent on this machine either.**
It is an Intel Core Ultra 7 265U: a 15 W laptop chip with 2 performance cores and 10 efficiency cores, at up to 5.4 GHz.
At a load of 17–22 every core sat at 400–900 MHz, so the CPU a fixed piece of work costs varies several-fold with the load and with which kind of core runs it.
With the decoding and layout counters reading the thread's CPU (`CLOCK_THREAD_CPUTIME_ID` on a locked thread), the unfocused city measured 1.11%, 1.14%, 1.17% and 1.32% of a core against 1%, down from 3.4% on wall time but still failing.
Layout is about 10 ms of thread CPU per snapshot, at 16 snapshots in 15 s.
Thread CPU never exceeds wall time, and the gate passed on wall time on a quiet machine, so the overage is clock speed and core type, not code.
`TestGroupingCostPerPrompt` already read process CPU, so the same applies to it.
**Aria's ruling (2026-10-22): count retired instructions.**
The cost gates count retired user-space instructions with `perf_event_open`, summing a counter on each of `cpu_core` and `cpu_atom` on this hybrid chip, and turn them into time with an instructions-per-second for "a core", measured once on this machine unloaded and written down with how it was measured.
Where there are no counters, the instruction check says it is skipped and the gate falls back to thread CPU; it never passes silently.
This applies to slices 1 and 2, and its test is that the instructions counted for the same work agree within a few percent at loads of about 0 and 20.

**Until slice 1 lands, the unfocused case does not gate** (the roadmap manager, 2026-10-22): it failed item 203's changelog-only landing on its own at 1.046%, and slice 1 waits on a quiet minute to calibrate `CoreRate`.
It still runs and states its number, and skips with "unmeasurable under load until item 209's instruction counts land (slice 1)", the honest form of item 194's "unmet", since it fails on clock speed rather than code.
Slice 1 restores it as a gate on instructions; the hidden case and the other gates are unchanged.
It landed as `c88744b` (r926).

**The same five runs failed the test two other ways, and both are the test measuring what load moves.**
Once the city's frame timer had not spoken within 60 s.
A focused, visible window first prints `FRAME` after 120 frames, which a virtual display draws in software: through a logging proxy, the city had its whole snapshot within 0.3–2.5 s, but its frame timer first spoke at 18, 20 and 34 s at loads of 12–20.
And once the hidden city read 138 KiB against less than 64 KiB.
That was not a whole snapshot, which is 225 KB: the run's decoding time was 21 ms, as in runs that read 7 KiB, and through the proxy three hidden runs read 7 KiB, 6 of it from the daemon.
`bytesRead` is `rchar`, every byte the city read from anything, including the X server and its files, so it measures more than the assertion means.

**`TestScriptsAreInTheCacheKey`'s "not cached" was not load.**
`go test` caches no run that opened a file modified under 2 s before, and the scratch copy was written just before its first run.
Slice 3 dates the copy an hour back and each probe's change a minute after the file's previous time, since Go keys an opened file by size, mode and modification time rather than contents.
