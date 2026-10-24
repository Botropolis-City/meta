# 232. The app's README and demo captions still describe the city before 0.2.0

**Open, in progress since 2026-10-24 in the session "item 232". Filed 2026-10-24 (r969), found by item 231's session while listing what the website gets wrong. Nobody's call — a defect in copy.**

[Item 231](231-the-website-still-talks-about-the-city-before-0-3-0.md) rewrites the website, but two of its sources live in botropolis and are stale the same way, and the site's rule is to quote the app rather than correct it.

- **`botropolis/README.md`.** Line 46 says *"A building's height is its context window used"*; since 0.2.0 a building's height is how much work its session has done, one to five storeys on your own scale. Its *Start here* (lines 13–14) starts the daemon with `systemctl --user enable --now botropolisd` and `botropolis install-hooks`; since 0.3.0 `botropolis setup` does both, and `install-hooks` is a deprecated name.
- **The demo scenarios' descriptions**, which `make media-import` copies into the site's `media.json` and the site shows verbatim: `demo/scenarios/timelapse.yaml`, `workday.yaml` and `metropolis.yaml` still say sessions are parked in, or leave for, the storage yard, which 0.2.0 removed (packed-up sessions are kept in the depot, `pkg/city/depot.go`), and `demo/README.md` line 17 says the same.

**The fix.** Rewrite each sentence from the app's own words: `pkg/city/depot.go`'s card for the depot, `pkg/state/state.go` for the states (`resting`, not parked), and the 0.2.0 and 0.3.0 changelog entries for height and `setup`.
Search the rest of `README.md`, `demo/` and `docs/` for *storage yard*, *parked*, *context window used* and *install-hooks* and fix every hit, except the changelog, which is a dated record.
Then run `make media-import` in botropolis.city so the site carries the new captions, without re-filming: only the descriptions change.
A test that fails on those phrases in `README.md` and the scenario descriptions keeps them from coming back.
