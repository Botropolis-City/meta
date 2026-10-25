# 246. The validation checklist was written for a city that no longer exists

**Open. Filed 2026-10-25 (r1024) at Aria's request. Nobody's call — Aria chose to rewrite it.**

[`validation-checklist.md`](validation-checklist.md) is ten steps for Aria to run against a live city, written on 2026-09-29 against a build at r293.
Since then parked containers became resting buildings, the storage yard became the depot, `d d` and the panels changed, and 0.3.0 moved commands (`status --live`, `attach`, `rm --older-than`, `setup`).
Steps 1 and 8 were run; the other eight have waited on Aria for four weeks and would no longer test what they say.

Aria, 2026-10-25, asked whether the checklist was still live: drop the plant's frames, and redo the checklist.

## The fix

1. Rewrite each step against the city as it is now, quoting keys and words from the app (`pkg/ui`, `pkg/city`, the manual pages), never from memory.
2. Run every step a script can: through the drive harness, `botropolis-demo`, or an acceptance test that already exists — and where one exists, say which test covers the step instead of keeping a manual step for it.
3. Leave for Aria only the steps that need her own terminal, notifications and desktop, each saying the keys to press and what she should see.
4. Take its bullet off `ROADMAP.md`'s *Waiting on Aria* list when the rewrite lands, and put one back only for the steps left to her.
