# 235. A caption change re-films its shots, and `--adopt` keeps the old caption

**Open, in progress since 2026-10-24 in the session "item 235". Filed 2026-10-24 (r973), from what items 231 and 232 found bringing new captions to the website. Nobody's call — a defect.**

[Item 232](232-the-apps-readme-and-demo-captions-predate-0-2-0.md) rewrote five demo captions, five description lines in `demo/scenarios/*.yaml` and nothing else, and [item 231](231-the-website-still-talks-about-the-city-before-0-3-0.md) had to rebuild `dist/demo/manifest.json` by hand to get them onto the site without re-filming.

**The mechanism.** In `botropolis/pkg/demo/cache.go`, `shotKey` hashes the whole `Shot` and the scenario without its shots, so a shot's `title` and `description` are part of its key: a caption-only change misses the cache and re-films the shot, which waits for a release, since a full re-film runs once per version.
The way round a key change, `film --adopt`, returns `cached.Media` as it was stored (`adopt`), with the old title and description; `recall` does the same on a hit.
So there is no way to change a caption without re-filming, and the manifest the site imports (`dist/demo/manifest.json`, git-ignored, written only by a film run) keeps the old words in every checkout until the next film.

**The fix.** Leave the words out of what the key hashes: a shot's key covers what changes its pixels, and its title and description change none.
On every recall or adopt, take each media's title and description from the current scenario, so `make film` on unchanged footage writes a manifest with today's captions in seconds.
Tests: changing only a shot's description keeps its key; a recalled and an adopted shot carry the scenario's current title and description; changing anything that draws still changes the key.

## Answered while building

- **The scenario's own description** (manager, 2026-10-24): left out of the key as well, by the item's rule that a key covers what changes pixels, provided nothing draws it; the session confirms by search that no drawing code reads a scenario's description or a shot's title or description, and that wherever a run writes a scenario's description into the manifest it takes the current one.
- **The test tree** (manager, 2026-10-24): approved as sent, `TestShotKey`, `TestFilmCache` and `TestAdopt` in `pkg/demo/cache_test.go`, one slice, no acceptance test.
