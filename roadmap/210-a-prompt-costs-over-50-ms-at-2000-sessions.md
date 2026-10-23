# 210. A prompt costs over 50 ms of CPU on the next load at 2,000 sessions

**Open. Filed 2026-10-23 (r924), from item 205. Nobody's call — the budget is set (item 158: 50 ms of CPU a prompt).**

Depends on: nothing

[Item 158](158-group-detection-reruns-pairwise-on-every-prompt.md) set grouping's cost at under 50 ms of CPU a prompt, and [item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md) made the pair cache linear. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) measured `TestGroupingCostPerPrompt`'s 2,000-session case on a settled home (directories a minute old, as a real home): **the whole load after a prompt takes 55–68 ms (median 60)**; a load with nothing changed 11–29 ms (median ~16); **the prompt adds 39–48 ms (median ~45)**, all at a machine load of 15–39. Item 205 lands that case in the self-removing "unmet" shape naming this item.
Item 198 listed what is left: the wording rebuilds document frequencies for every session, references are re-sorted, moved-word detection scans every word, and every group is named again, each O(n) per prompt.

## The fix

Make those per-prompt passes incremental in the number of sessions a prompt can affect, with item 158's from-scratch detector as the oracle. Measure with [item 209](209-cost-gates-fail-landings-on-a-busy-machine.md)'s instruction counts once they land, so machine load can't move the gate.

Tests: the 2,000 case reads under 50 ms (its skip removes itself); replays equal from-scratch at every step.
