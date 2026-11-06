# 349. Release 0.4.1

**Open. Filed 2026-11-06 (r1260) at Aria's request. Nobody's call — Aria named the version and what it holds.**

Depends on: 340, 343, 344, 345, 346, 347, 348

Aria, 2026-11-06, to the roadmap manager, on the six items she filed from dogfooding 0.4.0 on her laptop: *"let's do them as new versions"*,
and, offered 0.4.1 for the five fixes with 0.4.2 for item 348 after its frame rounds, she chose one version: *"One version, 0.4.1"*.

## What it holds

Items 343, 344, 345, 346, 347 and 348, filed 2026-11-05 from her own sessions,
and item 340, the rescan drift that 0.4.0 shipped red and [item 338](338-release-0-4-0.md) named for 0.4.1.
Fixes and features make a 0.x.Y under the pre-1.0 rule, so 0.4.1.
Everything else on `main` when its candidate is cut ships with it.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.4.0 did (item 338): one candidate, a landing freeze from it to the tag, the soak with its cycle phase, the re-film, S1–S10, L1–L2, A1–A7, the dry run, the release, the AUR packages and the site.
Manual checks stand across a re-cut; automated ones re-run.
The performance gate has to be green this time: item 340 is in the release for that reason.

## Open

- Item 348 is judged on frames, form by form, so it sets the release's pace.
  If Aria wants the fixes sooner, this item splits as first offered: 0.4.1 without 348, and 0.4.2 with it.
