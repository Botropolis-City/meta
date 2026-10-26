# 246. The validation checklist was written for a city that no longer exists

**Done 2026-10-26 (`1aa7ec4`, r1072). Filed 2026-10-25 (r1024) at Aria's request. Nobody's call — Aria chose to rewrite it.**

Depends on: nothing
Landed: slice 1 (`b16f210`, r1067).

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
- **An all-unpriced row** (manager): it says "cost unknown", the words the headline already uses when nothing prices (`Headline` in `pkg/stats/words.go`; first written here as "unpriced", corrected by the session).
- **Step 1's disagreement** (manager): filed as [item 250](250-a-session-running-a-background-command-says-it-needs-you.md), not fixed here.
- **The checklist on the release path** (Aria, 2026-10-25, asked by the manager): yes, before each release: `RELEASING.md` runs the checklist's steps left to Aria against the release build, between the soak and the re-film, and a release does not ship without it.
- **Background jobs with no conversation on disk** (manager): `claude agents --all` lists two done jobs with no transcript or session record, so the city has nothing to show; not shown, by design, and noted in step 1.

## Done

Three slices.

- **Slice 1** (`b16f210`, r1067, botropolis) made the steps a drive can run into tests.
  `TestEveryPanelClosesOnEscape` presses each of sixteen panel keys and then `esc`, and fails as item 137 did when a rung of the Escape ladder is removed.
  `TestTheAwayListOnRefocus` checks "While you were away" through a focus seam the drive can set, and fails when `watchFocus` stops opening it.
  `TestBreakdown` now holds the strip's day cost to the 24 h breakdown's, and `TestLayoutBreakdown` found a defect the old step 5 was looking for: a priced row none of whose messages had a price said "$0.00".
  It now says "cost unknown", with a changelog entry.
- **Slice 2** (`a2441b5`, this repository) rewrote [`validation-checklist.md`](validation-checklist.md) in three tiers: ten scripted checks each naming its tests, two live checks an agent runs against the real `claude` CLI, and six steps for Aria, A1 to A6, each with its keys and the words she should see.
  Step L1 was run live on 2026-10-25 and found the disagreement filed and fixed as [item 250](250-a-session-running-a-background-command-says-it-needs-you.md).
  *Waiting on Aria* now lists only her six steps, and the ten old steps and every dated run of them are kept as history.
- **Slice 3** (`1aa7ec4`, r1072, botropolis) put the checklist on the release path: `RELEASING.md` step 5 runs its live steps and Aria's against the release build, between the soak and the re-film.

**For Aria:** 0.3.1 was cut while slice 3 waited behind the release freeze, so its release run started before `RELEASING.md` named the checklist, and her steps A1 to A6 have not yet been run against any build.
