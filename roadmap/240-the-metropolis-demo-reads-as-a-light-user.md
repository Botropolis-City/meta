# 240. The metropolis demo reads as a light user since its sessions start hours apart

**Open, in progress since 2026-10-24 in the session "item 240". Filed 2026-10-24 (r1005) at Aria's request, on item 223's frames. Nobody's call — a defect in a demo.**

Depends on: nothing

[Item 223](223-the-staged-metropolis-names-most-districts-millrace.md) gave the staged scenarios start times that read like a real day, which ended the false groups, but the metropolis, staged as *"a heavy user's city"*, now reads light: its top bar's rates fell from about 15.3M/h fresh, 203M/h cached and 3.8M/h out to about 104k/h, 1.4M/h and 25k/h, since each session's tokens now spread over hours instead of its last minutes.
Aria, 2026-10-24, choosing *"Make it read heavy again"*.

## The fix

Make the metropolis read as a heavy user again without bringing back the false groups: busier transcripts (more turns, more tokens per turn, more sessions working), or starts that are closer together while still not within the group detector's minute, whichever reads truest.
Hold item 223's guard (each scenario's staged groups are exactly the ones it declares) and its `started:` rule.
Take the target rates from a real heavy history where one is to hand, or from the 0.3.0 metropolis's own top bar, and say which.

Tests: staging the metropolis gives top-bar rates within a stated band of the target, and the groups guard still holds; a before-and-after overview still for Aria.

## Answered while building

- **The cause** (the session "item 240", 2026-10-24): a session's rate is its total usage over the span from its first line to its last (`pkg/state/state.go`), and item 223's `started:` moves only the opening line back hours while the recording stays about ten turns in 25 seconds, so minutes of tokens spread over hours. Starts close enough to restore the rates would bring the false groups back.
- **The fix** (manager, 2026-10-24): a scenario-level `pace:`, set on the metropolis only, fills a paced session's gap from its opening to its recording with one main-line assistant turn per pace, carrying the recording's model and its own per-turn cache and output, and no text, tool call or prompt, so the group detector sees nothing new.
- **The target** (Aria, 2026-10-24): round, unattributed figures for "a heavy user" (5M/h fresh, 100M/h cached, 500k/h out, each within ×0.5 to ×2), never a real person's numbers, in the item or the tests. And the day's spend and message counts rise with the tokens (*"let it be honest"*).
- **The test tree** (manager, 2026-10-24): approved as sent, `TestStageFillsAPacedSessionsHours` in `pkg/demo/stage_test.go`, the `pace:` cases in `scenario_test.go`, and `TestStagedMetropolisReadsAsAHeavyUser` in `testing/integration/demo/` against those round targets, with item 223's groups guard unchanged.
