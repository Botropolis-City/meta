# 349. Release 0.4.1

**Open. Filed 2026-11-06 (r1260) at Aria's request. Nobody's call — Aria named the version and what it holds.**

Depends on: 343, 344, 345, 346, 347

Aria, 2026-11-06, to the roadmap manager, on the six items she filed from dogfooding 0.4.0 on her laptop: *"let's do them as new versions"*,
and, offered 0.4.1 for the five fixes with 0.4.2 for item 348 after its frame rounds, she chose one version: *"One version, 0.4.1"*.

## What it holds

Items 343, 344, 345, 346 and 347, filed 2026-11-05 from her own sessions: the fixes she can have before her workday.
Fixes make a 0.x.Y under the pre-1.0 rule, so 0.4.1.
Everything else on `main` when its candidate is cut ships with it.

**Split from the rest on 2026-11-06.**
This item first held items 340 and 348 too, then also the controls redesign, items 350 to 353 (Aria, through the design agent: *"I'd like this all to land in the next release whether it's 0.4.1 or 0.5.0."*).
Told that item 348's frame rounds and the controls chain put one release of all of it at a weekend's distance while the five fixes could land by morning, Aria chose: *"Do the split, but let's not soak until after 0.5.0"*.
So 348, 350 to 353 and 340 are [item 354, Release 0.5.0](354-release-0-5-0.md), and this one ships first.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) as 0.4.0 did (item 338), **with the soak waived** (Aria, 2026-11-06): one candidate, a landing freeze from it to the tag, the re-film, S1–S10, L1–L2, A1–A7, the dry run, the release, the AUR packages and the site.
The soak runs once, after 0.5.0, and covers both; item 354 carries it.
Manual checks stand across a re-cut; automated ones re-run.

The performance gate's rescan check (`TestARescanAtTwoThousandSessions`, item 340) was red at 0.4.0 and Aria shipped on it (*"Ship; soak now"*, 2026-11-03); nothing in this release touches the rescan, so it ships the same way and item 340 lands in 0.5.0.
If anything else in the gate is red, that is new and stops the release.
