# 246. The validation checklist was written for a city that no longer exists

**Open, in progress since 2026-10-25 in the session "item 246". Filed 2026-10-25 (r1024) at Aria's request. Nobody's call — Aria chose to rewrite it.**

[`validation-checklist.md`](validation-checklist.md) is ten steps for Aria to run against a live city, written on 2026-09-29 against a build at r293.
Since then parked containers became resting buildings, the storage yard became the depot, `d d` and the panels changed, and 0.3.0 moved commands (`status --live`, `attach`, `rm --older-than`, `setup`).
Steps 1 and 8 were run; the other eight have waited on Aria for four weeks and would no longer test what they say.

Aria, 2026-10-25, asked whether the checklist was still live: drop the plant's frames, and redo the checklist.

## The fix

1. Rewrite each step against the city as it is now, quoting keys and words from the app (`pkg/ui`, `pkg/city`, the manual pages), never from memory.
2. Run every step a script can: through the drive harness, `botropolis-demo`, or an acceptance test that already exists — and where one exists, say which test covers the step instead of keeping a manual step for it.
3. Leave for Aria only the steps that need her own terminal, notifications and desktop, each saying the keys to press and what she should see.
4. Take its bullet off `ROADMAP.md`'s *Waiting on Aria* list when the rewrite lands, and put one back only for the steps left to her.

## Answered while building

- **The plan and tree** (manager, 2026-10-25): approved. Steps already covered by tests become "scripted, see test X"; slice 1 adds a drive test that every panel closes on Escape and leaves the camera, a focus seam for the away list on refocus, and checks that the strip and the breakdown agree and that an all-unpriced row does not say `$0.00`; slice 2 rewrites the checklist.
- **An all-unpriced row** (manager): it says "unpriced", the word the headline already uses when nothing prices.
- **Step 1's disagreement** (manager): filed as [item 250](250-a-session-running-a-background-command-says-it-needs-you.md), not fixed here.
- **The checklist on the release path** (Aria, 2026-10-25, asked by the manager): yes, before each release: `RELEASING.md` runs the checklist's steps left to Aria against the release build, between the soak and the re-film, and a release does not ship without it.
- **Background jobs with no conversation on disk** (manager): `claude agents --all` lists two done jobs with no transcript or session record, so the city has nothing to show; not shown, by design, and noted in step 1.
