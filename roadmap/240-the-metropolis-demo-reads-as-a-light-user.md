# 240. The metropolis demo reads as a light user since its sessions start hours apart

**Open, in progress since 2026-10-24 in the session "item 240". Filed 2026-10-24 (r1005) at Aria's request, on item 223's frames. Nobody's call — a defect in a demo.**

Depends on: nothing
Landed: slice 1 (`dbfe84b`, r1008).

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
- **Slice 1's extra test** (the session "item 240", 2026-10-24, agreed): each filled turn writes what the recording's tool-only turns write (about 130–270 tokens), not the mean of all its turns, which put output at 2.5× the target.
- **A still shot before the ledger is read** (manager, 2026-10-24, slice 2 of this item): the paced metropolis's still showed $0.10 for the day where its stats store prices it at $153–196, since the headless `--screenshot` captures at the second frame after the first snapshot (`pkg/render/game.go` `capture`) without waiting for that snapshot's ledger read; with about 9,500 messages the read loses, so spend, wagons and building heft show a partly read day. That would mislead every still and clip filmed from a heavy corpus, the website's metropolis clips included, and Aria cannot judge "reads heavy" from it, so a still waits until the snapshot's ledger read is done, test first in `pkg/render`; Aria's stills come after it.
- **Slice 1's landing failed, and the plan changes** (manager, 2026-10-24): the heavier metropolis (about 9,565 messages) takes 19 s idle to read at the stats ingest's half a core (item 159), past the 30 s the frame tests allow under the gate's load, so they fail on item 202's guard ("opened at its ceiling, on a history not yet read"); no ceiling is raised and the 30 s stays. So: first a capture (`--screenshot`, `--record`) reads its history at full speed, since nobody waits on it and heavy captures run under the landing lock; and a capture that reaches the 30 s on an unread history fails outright, rather than opening on what was read. Then slice 1 lands with `pace: 45s` (about 3.3M/h fresh, 84M/h cached, 315k/h out, inside the band, about 13 s to read idle). The stale spend is [item 242](242-the-city-shows-a-partly-read-spend-after-its-first-read.md), a defect in the live city as well, which this session fixes under that number; the still-waits-on-Scan plan is dropped, since the capture already waits for `HeftsRead`. Aria's stills come after all three.
- **The full-speed capture read's tree** (manager, 2026-10-24): approved as sent, its own commit before slice 1. `Loader.WithFullSpeed()` reads the stored hefts and the later read at the whole clock for a `--screenshot` or `--record`; `TestPacedPasses` gains the full-speed cases ("it should not sleep"), and `TestACaptureFailsAtTheCeiling` replaces "it should open" with failing the capture, naming the unread history, at the 30 s ceiling. The wiring from a capture flag to the full-speed source gets a unit test if `pkg/app` has a seam for it, and otherwise rests on the acceptance tests, said in the commit.
