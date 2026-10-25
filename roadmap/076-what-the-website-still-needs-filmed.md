# 76. What the website still needs filmed

**Open, in progress since 2026-10-25 in the session "item 76". Filed 2026-10-10 (r376), when botropolis.city was rebuilt around the demo media. Nobody's call — each is a scenario or a filming option, and each replaces a stand-in the site already ships.**

Depends on: nothing
Landed: slice 1 (`68cf851`, r1025).
Landed: slice 2 (`f92878e`, r1029).
Landed: slice 3 (`131cff1`, r1034).

The site lives in its own repository, `Botropolis-City/botropolis.city`, checked out beside botropolis under the meta repository's root, at `botropolis.city/` (until 2026-10-15, `~/workspaces/github/botropolis.city`).
It reads `dist/demo/manifest.json` through `make media-import` there, so anything below reaches the site with `make media-import media-upload` and a push.

1. **A hero loop.** The title screen is `metropolis/hero.png` with a CSS drift, because every clip carries the interface and none loops.
   Wanted: the metropolis with the interface hidden, 12–16 s, a slow drift or turn whose last frame is its first, 3 MB or less. A 4:5 crop for phones is a bonus.
2. **A still per view.** The nine-view switcher is frames of `layers/views.mp4` at hard-coded seconds (`tools/import-media.ts` in the site repo), so refilming that clip can move them.
   Wanted: one still per view (attention, spend, pressure, staleness, servers, traffic, models, fan-out, health), plus night and a plain day, all from the `layers` camera.
3. **A social card.** `og:image` is `metropolis/hero.png` cropped to 1200×630 by the site build.
   Wanted: a 1200×630 shot framed for it, interface hidden.
4. **Posters from a chosen frame.** `timelapse/day.png` caught the drawn pointer mid-hover over the power plant, because a clip's poster is whatever frame it lands on.
   Wanted: a `poster_at` on a shot.
5. **Anchors, optionally.** The site's hotspot map is placed by hand in percentages (`src/data/glance.ts`), and moves out of true whenever the metropolis is refilmed.
   Wanted: the manifest carrying the screen position of named objects in each still — the plant, the towers, the storage yard, the fountain, each district — so the hotspots follow the frame.

The night stills are held back by item 74, not by anything here.

## Answered while building

- **When to film** (Aria, 2026-10-25, asked by the manager): build the filming options now (the looping hero, a still per view, the social card, `poster_at`, anchors) with their tests, and film once at the next release, as her once-per-release rule says; the site gets the media then.
- **The slices** (manager, 2026-10-25): `poster_at`; a still per view, every entry of `city.Views` including groups, reached by the lens keys derived from `city.Lenses` rather than a city flag, with the chrome kept and a separate plain day with the interface hidden; the social card; the looping hero; anchors; and last, the site's import in botropolis.city against a manifest fixture, with the anchors feeding item 231's hotspot tests rather than replacing them.
- **The hero loop** (manager, 2026-10-25): slice 3's design and tree approved: a `home` pan target the player resolves from its own pans; `loop: {crossfade: 1}` recorded with a lead and blended in Go on the PNG frames, so the last frame leads into the first; `max_mb` re-encoding at rising CRF up to a named ceiling, refusing GIFs; `crops: ["4:5"]` from the middle of the frame. The crossfade's ghosting of movers is a seam to show Aria when it is filmed.
