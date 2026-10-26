# 274. A session whose transcript was deleted stays on the map

**Fixed 2026-10-26 (`ad89e08`, r1103). Filed 2026-10-26 (r1099), from Aria's other laptop (item 270). Nobody's call — Aria ruled.**

`pkg/state/loader.go` catalogues every stopped session, however old: time ages a session and never takes it off the map.
The catalogue (`sessions.json`) keeps a session after its transcript is gone, so the 489 temporary-directory sessions on Aria's other laptop, whose transcripts no longer exist, are all still drawn.

Aria, 2026-10-26: *"Make this a setting. When the transcript is gone sessions leave by default, but we can toggle showing them."*

## The fix

1. A session whose transcript no longer exists **leaves the map** at the next load, by default.
2. A setting keeps them, as today.
3. Statistics already recorded for it are kept; only the building goes.
4. Tests: a catalogued session whose transcript is deleted is not drawn by default; with the setting on, it is; a session whose transcript exists is untouched; and the catalogue drops nothing it needs to bring the session back if the setting is turned on.

## Answered while building

- **The design** (session's, approved by the manager, 2026-10-26): the ledger already keeps every entry and marks a transcript-less one `ConversationGone`; the city drops those in `Scene.restate` unless `gone_sessions` (bool, default false, settings row *deleted transcripts*) is on, so toggling is live and the ledger and statistics are untouched. The filter is a shared `pkg/city/onmap.go` that item 273 extends.

## Closed

Fixed in `ad89e08` (r1103), with the hostile config's new key in `2bb7da2` (r1104).
The city, not the daemon, leaves the session off: `city.Shown` filters the snapshot in `Scene.restate`, so the setting toggles live from the panel without restarting the daemon, which reads its config only at start.
The ledger (`sessions.json`) and the statistics store are untouched, so turning the setting on brings every such session back at once and the spend reads as before.
The setting is `gone_sessions` (default false) and the settings panel's *deleted transcripts* row, hidden or shown.
Item 273 adds its scripted runs to the same `Shown`.
Tests: `pkg/city/onmap_test.go` (hidden by default, no district made only of them, shown with the setting, live toggle, spend unchanged, a session with a transcript untouched), `pkg/state/loader_test.go` (the ledger keeps the entry), `pkg/config`, `pkg/app` and `pkg/render` for the key, row and live apply.
No frame: nothing new is drawn.
