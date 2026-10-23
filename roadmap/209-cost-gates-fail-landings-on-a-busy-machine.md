# 209. Cost gates fail landings at random while the machine is busy

**Open, in progress since 2026-10-22 in the session "item 209". Filed 2026-10-22 (r921), from item 203's landing. Nobody's call — a defect in the gates; every landing runs them.**

Depends on: nothing

Item 203's changelog-only landing failed on three gates that measure cost, none of which its change touches, and a rerun alone at a load of 15–19 failed again:

- **`TestAnUnwatchedCityUnderAStreamOfSnapshots`** ([item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md)): hidden 1.19% against 1%, then unfocused **3.4% against 1%**. The unfocused case gates the city's own counted decoding and layout time, which is **wall-clock** inside the process, so machine load moves it directly.
- **`TestGroupingCostPerPrompt`** ([item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md)): 52.8 ms against 50.
- **`TestScriptsAreInTheCacheKey`**: "not cached", a flake of its own.

A gate that a busy machine fails is not measuring the code, and it fails other items' landings at random — the cost every session pays while several build at once.

## The fix

Measure CPU, not wall time, wherever a gate means CPU: the decoding and layout counter reads the thread's CPU time (`RUSAGE_THREAD`, or `CLOCK_THREAD_CPUTIME_ID` on a locked thread) rather than elapsed time; per-prompt grouping cost the same. Where a gate must read process CPU, take the quieter of two windows, as [item 196](196-a-settled-daemon-bursts-to-several-cores-on-rescans.md) did. Look at `TestScriptsAreInTheCacheKey`'s "not cached" separately.
The limits stay as they are (gate on targets); only what is measured changes.

Tests: each gate passes its own red-check (the pre-fix code still fails it) and passes at a load of ~30 on this machine (run beside a `make test` of another worktree), five runs in a row.
