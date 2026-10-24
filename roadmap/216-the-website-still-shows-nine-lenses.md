# 216. The website still shows nine lenses, and its media import fails on the new views clip

**Fixed 2026-10-23 (botropolis.city `71f908e`, r30). Filed 2026-10-23 (r966), from the 0.3.0 re-film. Nobody's call — a defect; the 0.3.0 website update waited on it.**

Depends on: nothing

[Item 177](177-the-layers-stills-show-the-wrong-lenses.md) changed the demo's `layers` shots to the city's six lenses: the `views` clip now runs 24.5 s, pressing the lens key, then 2–6 and 1 (work, cost, capacity, health, connections, attention), then `N` twice for night and back (`botropolis/demo/scenarios/layers.yaml`), and the old `spend` and `pressure` stills became `cost` and `capacity`.
The website was never updated to match. `make media-import` in botropolis.city now fails on the 0.3.0 film: `tools/import-media.ts`'s `viewFrames` still lists ten old lenses with frame times up to 30 s, so ffmpeg returns nothing past the clip's end ("Input Buffer is empty"). `src/components/Views.astro` still says "Nine ways to read the city", and `src/data/media.json` still names `layers-pressure`, `layers-spend` and the old `views-*` stills.

## The fix

Take the lenses and their frame times from the scenario rather than a hand-kept list: read `layers.yaml`'s `views` script (each key's time, plus a settle) and the lenses' own titles and descriptions as the city states them (`botropolis/pkg/city/lens.go`), so the next change to the lenses cannot leave the site behind. Rename the section to match ("Six ways to read the city"), point the layer stills at `cost` and `capacity`, and drop what no longer exists.

Tests: an import test that fails when a frame time is past its clip's length, or a lens on the page isn't one the city has; the site's page tests pass with the new media; and a frame of the views section for Aria.

## Fixed

`tools/views.ts` in botropolis.city now reads the lenses, their order and their sentences from `pkg/city/lens.go`, and each frame's second from the `views` shot in `layers.yaml`: half a second before the next key, or before the clip's end for the last.
The import refuses a frame past the clip's end, a key for a lens the city does not have, and a lens the clip never shows.
The section takes its title from the shot ("Six ways to read the city"), each lens's question is its `About()` sentence verbatim, and night's is the `night` shot's description.
The tabs read 1–6 and n, as the app's keys do.
Media was re-imported from the 0.3.0 film, so the layer stills are `cost` and `capacity` and the old `views-*` stills are gone.

Tests: `tools/views.test.ts` runs against fixture copies of `lens.go` and `layers.yaml`, since the site's CI has no botropolis checkout, plus one test against the live files that runs when `BOTROPOLIS_DIR` exists and is skipped by name when it does not.
Three page tests check the title, the seven tabs and a lens's question.
The site's CI run 40057545671 passed and deployed, with 94 page tests green against the uploaded clips.

The frame of the views section, with Cost chosen, went to Aria through the roadmap manager.
One deviation: the caption names night "Night", and its alt text reads "The city at night", because night is not a lens.
