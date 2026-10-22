# 198. Group detection's pair cache grows with the square of every session ever shown

**Open, in progress since 2026-10-22 in the session "item 198". Filed 2026-10-21 (r876), found by item 196. Nobody's call — a defect against the daemon's memory budget.**

Depends on: nothing

[Item 158](158-group-detection-reruns-pairwise-on-every-prompt.md) made group detection incremental by caching every pair's score (`group.scorePair`). Item 196 measured it with **2,000 small sessions: the pair cache holds 415 MB live**, above the daemon's 256 MiB memory limit, so the collector runs back to back at 200–350% of a core.
The pairs are n² over every session ever shown, and `d.next` is rebuilt in full on each detection. Aria's home has about 185 transcripts and does not hit it; a heavy user does.

## The fix

Keep only the pairs that can matter: those that share a signal (a directory, a branch, a file, a word above the rarity floor), found through an index rather than by enumerating every pair, and drop pairs whose sessions have aged out of the 30-day window. Update `d.next` in place rather than rebuilding it.
Item 158's from-scratch detector stays the oracle.

Tests: with 2,000 synthetic sessions, the daemon stays under its memory limit (live heap) and the settled CPU budget; detection results equal from-scratch at every step of a replay, as item 158's tests do; a benchmark of the cache's size against session count, which should grow about linearly.
