# 76. What the website still needs filmed

**Done 2026-10-25 (botropolis.city `9b32354`, r1037). Filed 2026-10-10 (r376), when botropolis.city was rebuilt around the demo media. Nobody's call — each is a scenario or a filming option, and each replaces a stand-in the site already ships.**

Depends on: nothing
Landed: slice 1 (`68cf851`, r1025).
Landed: slice 2 (`f92878e`, r1029).
Landed: slice 3 (`131cff1`, r1034).
Landed: slice 4 (`d1f2d94`, r1035).
Landed: slice 5 (`2c386f2`, r1035).
Landed: slice 6 (`a85bc40`, r1035).
Landed: slice 7 (`9b32354`, r1037).

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
- **The site's side** (manager, 2026-10-25): slices 5–7 in botropolis.city, against manifest fixtures: view stills replacing frames cut from `layers/views`, the looping hero and social card, and anchors placing item 231's hotspots with its pixel check unchanged; until the release films, each falls back to today's stand-in and the import names which, and every push is checked against production as unchanged. The film makes all 10 views and the site imports its 6 lenses' first views and night; the plain day has no place on the page yet. Whether the site shows more is Aria's at the release. No plaza anchor: its middle is the fountain.

## Done

Everything the item asks for is built and tested, and nothing is filmed yet: the next release's film makes it, as Aria ruled.
Slices 1–4 are in botropolis, and 5–7 in botropolis.city.

1. **The hero loop**: metropolis `loop`, 15 s, interface hidden, a pan out to driftwood and back to `home`, with a 1 s crossfade so its last frame leads into its first, `max_mb: 3`, and a 4:5 crop (slice 3).
   On the site, the title screen plays it muted and looped, with the crop on a phone, and never starts it for reduced motion (slice 6).
   `home` ended up in the game, not the player, as the world point in the middle when the clip began, because the scene clamps pans and a tally of them would overshoot.
2. **A still per view**: `layers` films one still of every entry in `city.Views`, ten of them, with the chrome on, plus a plain day with the interface hidden, and night (slice 2).
   The site shows each of its six lenses' first view and night (slice 5).
   `testing/integration/demo/media_test.go` fails when the city gains a view without a still.
3. **The social card**: metropolis `card`, 1200×630, interface hidden (slice 2), used as the link preview as filmed (slice 6).
4. **`poster_at`** on a shot (slice 1); `timelapse/day` takes its poster at 41 s.
5. **Anchors**: every still's manifest entry carries where the plant, fountain, library, hall, depot, each tower and each district landed (slice 4), and the map key's towers, library, plant, depot and district hotspots stand at them (slice 7).
   Item 231's pixel checks pass on a metropolis hero filmed locally with anchors, with those hotspots placed from the anchors.

Until the release films, the site shows today's stand-ins, and `make media-import` lists them: the hero still with its drift, hand-placed hotspots, the hero cropped for the link preview, and view frames cut from `layers/views`.
After each site push, `make verify` and the 137 page tests passed against production, and the live markup stayed identical.

For Aria at the release: the loop's seam, where a train or boat that has moved is ghosted for its last second; whether the 4:5 crop suits the phone layout; and whether the site should show the other four views or the plain day.
