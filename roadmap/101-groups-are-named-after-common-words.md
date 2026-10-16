# 101. Groups are named after common words

**Open, in progress since 2026-10-16 in the session "item 101". Filed 2026-10-16 (r521) at Aria's request, from a frame of item 90's. Nobody's call — a defect.**

A group is named from the reference it shares and its members' most distinctive words, and in `docs/screenshots/r515-item-90-lines.png` that came out as "PROJ-123 · through allow", from prompts that said "Allow the headers through".
Neither word says what the work is.

Where it comes from: `pkg/group/name.go` (`detection.name`) takes the words that weigh most by rarity across the history (`pkg/group/wording.go`), after a hand-written stop-word list of about eighty words.
"through" and "allow" are not on it, and on a small history any word that appears in few sessions weighs as rare, so ordinary English verbs and prepositions win over the nouns that name the work ("headers"), and the two winners are shown in rank order rather than the order they were said.

The fix, cheapest first:

- a full English stop-word list rather than a hand-picked one;
- prefer words shared by more than one member over a word only one member said;
- show the chosen words in the order they first appear in the members' prompts.

Tests: data-driven over prompt sets, including the one in the frame, the name should hold the work's nouns ("rate-limit headers") and none of the stop words; and the wording signal's measured false-join rate (item 87's 1%) must not rise, since the same weights decide grouping.
Renaming stays the only naming anyone has to do, so this only improves the guess.
