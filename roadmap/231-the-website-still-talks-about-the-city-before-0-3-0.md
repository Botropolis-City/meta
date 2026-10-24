# 231. The website still talks about the city as it was before 0.3.0

**Open, in progress since 2026-10-24 in the session "item 231". Filed 2026-10-24 (r969) at Aria's request. Nobody's call — Aria ruled on how it ships, below.**

Aria, 2026-10-24: *"Since 3.0.0 was such drastic changes, we should update the website and its rhetoric accordingly. Not just the assets. Have an agent do that and release it."*
The release she means is botropolis `v0.3.0`, tagged 2026-10-23; there is no 3.0.0.
Asked whether the agent should show her the copy before deploying, she chose *"Deploy, then show me"*.

**Where the site stands.** The assets are current: the timelapse was re-filmed for 0.3.0 (`59b6a0f` in botropolis.city), and the views section reads the city's six lenses ([item 216](216-the-website-still-shows-nine-lenses.md)).
The words are not.
The hero (`src/components/Hero.astro`) has not changed since 2026-10-10, before 0.2.x, and nothing on the page says what 0.3.0 changed.

**What 0.3.0 changed**, from `botropolis/CHANGELOG.md`'s `[0.3.0]` section, which is the source for every claim:
- it is a performance release, with numbers measured on a laptop's integrated graphics: a frame in about 10–11 ms, about 445 MiB settled instead of up to 4.6 GiB in 0.2.2, a hidden city under 1% of a core, the daemon settled under 1%, and a map about a second after the first launch;
- sharing mode (`shift+s`), which hides what identifies you so the city can be posted;
- manual pages, and `docs/compatibility.md`'s promise of what 1.0.0 will not break;
- commands that moved (`status --live`, `attach`, `rm --older-than`, `setup`), and the daemon restart an upgrade needs.

## The fix

1. **Read before writing.** The whole page, every component in `src/components/`, `botropolis/CHANGELOG.md` from 0.2.0 to 0.3.0, `botropolis/README.md` and `botropolis/DESIGN.md`.
   Make a list of every sentence on the site that 0.3.0 made false, stale or understated, and every 0.3.0 change a visitor would care about that the site leaves out.
2. **Rewrite the rhetoric**, not only the facts: the hero, the page's description and social text, each section's lead, the install section and the footer, so the page reads as the app 0.3.0 is.
   - Every number quotes the changelog, with the machine it was measured on; never round a number up, and never claim a budget 0.3.0 misses (the changelog names two).
   - Copy about the city comes from the app, as `botropolis.city/CLAUDE.md` says: view names, hover cards and colours are quoted from `pkg/city` and `pkg/ui`, never paraphrased.
   - Write for anyone who uses Claude Code, not only developers: a project is a directory, and git, branches and pull requests are things the city shows when they exist, never assumptions.
   - Install commands must match 0.3.0's (`botropolis setup`, the restart after upgrading) and the packages `pkg.botropolis.city` serves.
3. **Release it.** `make lint` and `make test` in botropolis.city, then push to `main` and `make site-deploy` (its token comes through `secret-run`, so a prompt comes up for Aria), then `make verify` against the live domains.
   Nothing in `infra/` changes; if the work finds it needs to, that goes back to the manager first.
4. **Show Aria.** Send the manager the live URL, a full-page frame at desktop and at phone width, and a before-and-after of every sentence that changed, so she can ask for changes.

Tests: the site's acceptance tests pin some copy; change them with the copy, test first where a test asserts a claim (for example, that every number on the page appears in the changelog it cites, if such a check is cheap to add).

## Answered while building

- **Step 1's list and the test tree** (manager, 2026-10-24): approved as sent, items 1–14 and the rewrite. Rhetoric may characterise but never exceed the changelog: "light enough to leave open" is true of a hidden or unfocused city (under 1% of a core), not a focused one (about half a core), so it says which.
- **What lives in the app** (manager, 2026-10-24): the app's README and the demo scenarios' captions are filed as [item 232](232-the-apps-readme-and-demo-captions-predate-0-2-0.md); this item ships with the captions as they are, and 232's `make media-import` updates them.
