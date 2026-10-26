# 274. A session whose transcript was deleted stays on the map

**Open. Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — Aria ruled.**

`pkg/state/loader.go` catalogues every stopped session, however old: time ages a session and never takes it off the map.
The catalogue (`sessions.json`) keeps a session after its transcript is gone, so the 489 temporary-directory sessions on Aria's other laptop, whose transcripts no longer exist, are all still drawn.

Aria, 2026-10-26: *"Make this a setting. When the transcript is gone sessions leave by default, but we can toggle showing them."*

## The fix

1. A session whose transcript no longer exists **leaves the map** at the next load, by default.
2. A setting keeps them, as today.
3. Statistics already recorded for it are kept; only the building goes.
4. Tests: a catalogued session whose transcript is deleted is not drawn by default; with the setting on, it is; a session whose transcript exists is untouched; and the catalogue drops nothing it needs to bring the session back if the setting is turned on.
