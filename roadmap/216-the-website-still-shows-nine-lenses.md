# 216. The website still shows nine lenses, and its media import fails on the new views clip

**Open, in progress since 2026-10-23 in the session "item 216". Filed 2026-10-23 (r966), from the 0.3.0 re-film. Nobody's call — a defect; the 0.3.0 website update waits on it.**

Depends on: nothing

[Item 177](177-the-layers-stills-show-the-wrong-lenses.md) changed the demo's `layers` shots to the city's six lenses: the `views` clip now runs 24.5 s, pressing the lens key, then 2–6 and 1 (work, cost, capacity, health, connections, attention), then `N` twice for night and back (`botropolis/demo/scenarios/layers.yaml`), and the old `spend` and `pressure` stills became `cost` and `capacity`.
The website was never updated to match. `make media-import` in botropolis.city now fails on the 0.3.0 film: `tools/import-media.ts`'s `viewFrames` still lists ten old lenses with frame times up to 30 s, so ffmpeg returns nothing past the clip's end ("Input Buffer is empty"). `src/components/Views.astro` still says "Nine ways to read the city", and `src/data/media.json` still names `layers-pressure`, `layers-spend` and the old `views-*` stills.

## The fix

Take the lenses and their frame times from the scenario rather than a hand-kept list: read `layers.yaml`'s `views` script (each key's time, plus a settle) and the lenses' own titles and descriptions as the city states them (`botropolis/pkg/city/lens.go`), so the next change to the lenses cannot leave the site behind. Rename the section to match ("Six ways to read the city"), point the layer stills at `cost` and `capacity`, and drop what no longer exists.

Tests: an import test that fails when a frame time is past its clip's length, or a lens on the page isn't one the city has; the site's page tests pass with the new media; and a frame of the views section for Aria.
