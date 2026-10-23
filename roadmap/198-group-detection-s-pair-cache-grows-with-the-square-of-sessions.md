# 198. Group detection's pair cache grows with the square of every session ever shown

**Fixed 2026-10-22 (`c9f119a`, r916). Filed 2026-10-21 (r876), found by item 196. Nobody's call — a defect against the daemon's memory budget.**

Depends on: nothing
Landed: slice 1 (`4f0cdb1`, r906).
Landed: slice 2 (`c9f119a`, r916).

[Item 158](158-group-detection-reruns-pairwise-on-every-prompt.md) made group detection incremental by caching every pair's score (`group.scorePair`). Item 196 measured it with **2,000 small sessions: the pair cache holds 415 MB live**, above the daemon's 256 MiB memory limit, so the collector runs back to back at 200–350% of a core.
The pairs are n² over every session ever shown, and `d.next` is rebuilt in full on each detection. Aria's home has about 185 transcripts and does not hit it; a heavy user does.

## The fix

Keep only the pairs that can matter: those that share a signal (a directory, a branch, a file, a word above the rarity floor), found through an index rather than by enumerating every pair, and drop pairs whose sessions have aged out of the 30-day window. Update `d.next` in place rather than rebuilding it.
Item 158's from-scratch detector stays the oracle.

Tests: with 2,000 synthetic sessions, the daemon stays under its memory limit (live heap) and the settled CPU budget; detection results equal from-scratch at every step of a replay, as item 158's tests do; a benchmark of the cache's size against session count, which should grow about linearly.

## Closed

Fixed in two slices, `4f0cdb1` (r906) and `819233f`/`c9f119a` (r915–916), with the changelog entry after them.

**Slice 1, the cache.** Every signal `pair` reads is indexed (directory and visits by path and ancestors, references, team, parent, messages, rare words, branch and its tickets, files, pastes by a prefix of their sorted shingle hashes, starts and closes by time), and only a changed session's candidates are scored.
The cache keeps only the pairs that scored, under both sessions, updated in place: a changed or departed session's ties are dropped and its candidates scored again.
At 2,000 sessions it keeps 3.8 pairs and about 3 KB per session, flat from 250 (`BenchmarkPairsKept`), where it kept all 1,999,000; `TestPairCache` allows 20 pairs a session, a session tied to at most 40 others.

**Slice 2, the passes around it.** Once the cache stopped dominating, a prompt among 2,000 sessions cost 1.1 s, almost all of it in passes that were O(n) or worse on every prompt.
`suggest` searched every group for every edge, the wording recounted every word, every group was named again, `matchStored` compared every remembered group with every new one, and the loader copied every session each load.
Each is incremental or indexed now: 7.6 ms and 2 MB a prompt in `BenchmarkDetectAfterAPromptAmongMany`, and a first detection of 2,000 sessions allocates 20 MB.

The tests that show it:
- `pkg/group/detector_test.go` holds the detector to item 158's detector, which is now a test file, `oracle_test.go`, with its own sort, clustering, groups, memberships, remembered ids and suggestions as they were at r905.
  The cases are each signal alone, 40 random histories mixing every signal through one detector, one session changing at a time, the replay prompt by prompt, remembered groups that tie, overlap or repeat a session, a not-related pair a third session ties, and a group named after its directory moving.
  The in-place cache is also held to what a fresh one keeps after every change.
- `TestDaemonWithTwoThousandSessions` runs the daemon on the synthetic home plus 2,000 small sessions: a live heap of 20–24 MB (443 MB with slice 1 reverted, which fails it) and 59–63 MiB of Private_Dirty, both gated.
- `TestGroupingCostPerPrompt` runs at 2,000 sessions as well as 100, and gates what a prompt adds to a load at 50 ms: 15–35 ms there on a busy machine.

Every index lookup and every rewritten check was mutated and fails the tests, apart from one equivalent mutant noted in `819233f`.

Deviations, for Aria:
- **The settled CPU budget is not met at 2,000 sessions, and not because of grouping.** The daemon uses 5.8–8.9% of a core there against 2%, and grouping is about a sixth of it; the rest is each rescan's load, which grows with every transcript on disk.
  That case and the whole load after a prompt (37–60 ms against 50) are in the unmet shape, printing their numbers and naming [item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md), which the roadmap manager filed for it.
- **Private_Dirty is gated but close**: 59–63 MiB against 64, mostly outside grouping (the synthetic home alone is 19 MiB, and the startup peak is kept until Go's scavenger returns it, since the daemon releases memory only after hook events).
- **Slice 2 went further than the item asked**, into suggestions, naming, the wording and the loader, because the 2,000-session measure the item asked for found them.
