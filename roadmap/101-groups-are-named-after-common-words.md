# 101. Groups are named after common words

**Fixed 2026-10-16 (`0397d66`, r542). Filed 2026-10-16 (r521) at Aria's request, from a frame of item 90's. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`0397d66`, r542).

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

## Answered while building

- **The cause** (item 101's session, 2026-10-16): two of the three fixes above were already in the code; the naming weight dropped every word found in more than half of all sessions, so on a small history the group's own words were cut and one member's leftovers named it.
- **The fix** (manager, 2026-10-16): a full stop-word list, carried in the source under its licence; and naming measures a word's rarity against the sessions outside the group, taking only words a larger share of members use than outsiders, ranked by how many members said them; first-said order stays.
- **The false-join rate** (manager, 2026-10-16): a test cannot read a real history, so the wording signal's rate is measured before and after on this machine, in memory, and recorded here; a rise stops the landing. Before: 1.05% of random pairs (380 sessions), 12.19% of pairs started within 15 minutes.
  After, with the full stop-word list (the only part that touches the signal): 0.93% of random pairs (186 of 20,000, 380 sessions), 12.19% of pairs started within 15 minutes — the false joins fell and the real ones held.
- **The test tree** (manager, 2026-10-16): approved as proposed, data-driven over prompt sets in `pkg/group/name_test.go`, plus a stop-words-only case in `pkg/group/wording_test.go`.

## Closed

Fixed 2026-10-16 in `0397d66` (r542): a group is named by the words more of its members use than the sessions outside it, ranked by how many members said them and shown in the order they were said, after Snowball's English stop-word list (shipped under its BSD licence in `pkg/group/stopwords/`) joined the hand-written one.
The data-driven name tests, including the frame's prompt set, failed first and pass now.
The changelog's unreleased groups entry says so (`e3e8d99`).

The wording signal's false-join rate fell rather than rose: 1.05% of random pairs before, 0.93% after (186 of 20,000, 380 sessions on this machine, 2026-10-16), with pairs started within 15 minutes unchanged at 12.19%.

The frame is `docs/screenshots/r542-item-101-lines.png` (`e111610`), and it passed (Aria, 2026-10-16): the line reads "PROJ-123 · rate-limit headers".
Its scene was rebuilt rather than reused, because r515's synthetic home was never kept: the same districts and PROJ-123 prompts, with one "Allow the headers through", staged in an isolated runtime directory.
It has no foreman, pull request or recaps, so it shows the line and its name, not a copy of r515.
