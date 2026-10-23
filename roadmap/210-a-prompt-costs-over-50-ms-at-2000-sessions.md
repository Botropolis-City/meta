# 210. A prompt costs over 50 ms of CPU on the next load at 2,000 sessions

**Fixed 2026-10-23 (`aad7833`, r950). Filed 2026-10-23 (r924), from item 205. Nobody's call — the budget is set (item 158: 50 ms of CPU a prompt).**

Depends on: nothing
Landed: slice 1 (`aad7833`, r950).

[Item 158](158-group-detection-reruns-pairwise-on-every-prompt.md) set grouping's cost at under 50 ms of CPU a prompt, and [item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md) made the pair cache linear. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) measured `TestGroupingCostPerPrompt`'s 2,000-session case on a settled home (directories a minute old, as a real home): **the whole load after a prompt takes 55–68 ms (median 60)**; a load with nothing changed 11–29 ms (median ~16); **the prompt adds 39–48 ms (median ~45)**, all at a machine load of 15–39. Item 205 lands that case in the self-removing "unmet" shape naming this item.
Item 198 listed what is left: the wording rebuilds document frequencies for every session, references are re-sorted, moved-word detection scans every word, and every group is named again, each O(n) per prompt.

## The fix

Make those per-prompt passes incremental in the number of sessions a prompt can affect, with item 158's from-scratch detector as the oracle. Measure with [item 209](209-cost-gates-fail-landings-on-a-busy-machine.md)'s instruction counts once they land, so machine load can't move the gate.

Tests: the 2,000 case reads under 50 ms (its skip removes itself); replays equal from-scratch at every step.

**The interim shape can't fail** (manager, 2026-10-23): item 205 landed the 2,000 case as "skip naming 210 while over 50 ms, pass under", because it reads 42–60 ms with machine load and the self-removing shape flipped. That case now has no way to fail: a regression to 200 ms would skip. Until this item lands, it needs a regression ceiling that fails (today's worst plus a margin, named as a ceiling, as item 194 did), or item 209's instruction counts so the reading stops moving with load.

## Closed

Fixed in one slice, `aad7833` (r950), with the changelog entry in `874d9bf` (r952).

The detector keeps its candidate index from run to run and patches it for the sessions a prompt changed, rather than scanning every session's words against the changed one's; the sessions using a word whose rarity moved are found through the same index.
When the sessions are in the same order and memory sits out and keeps apart the same ones, the last run's sorted edges are kept but for the changed sessions', which are merged back in, rather than every tie being walked and every edge sorted again.
Anything else takes the full pass, as before.

The tests that show it:
- `TestGroupingCostPerPrompt`'s 2,000 case is a gate again, with no skip and no ceiling: medians of 15–19 ms at a machine load of 9–15, where main's code read 17–48 ms in runs alternating with it.
- `pkg/group/detector_test.go` holds the edges to item 158's from-scratch detector while memory changes between runs and while sessions join and leave, and the patched index to a fresh detector's at every step, alongside the replays already there.
  Leaving out the removal of a session's old keys, the order check, the memory check or the filter on changed sessions' edges each fails them.
- `BenchmarkDetectAfterAPromptAmongMany`: 10–17 ms to 4–7 ms, and 6,566 allocations to 2,521.

Deviations, for Aria:
- **It measures process CPU, not item 209's instruction counts**, which had not landed (manager, 2026-10-23); item 209 converts the test when its slice 1 lands, and touched nothing here.
- **The index costs about 1.2 KB a session more** (`BenchmarkPairsKept`, 3.6 to 4.8 KB live, flat with session count): about 2.4 MB at 2,000 sessions, beside the Private_Dirty case [item 211](211-the-statistics-store-adds-21-mib-at-2000-sessions.md) holds.
- Wording's per-session pass, references and naming are still O(n) a prompt, as item 198 listed; at 2,000 sessions the load no longer needs them cut.
