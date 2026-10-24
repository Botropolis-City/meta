# 242. The city shows a partly read day's spend for up to 30 seconds after its first read

**Fixed 2026-10-24 (`fec9e4b`, r1010). Filed 2026-10-24 (r1006), found by item 240's session. Nobody's call — a defect; item 240's session fixes it.**

Depends on: nothing
Landed: slice 1 (`fec9e4b`, r1010).

`pkg/stats/ledger.go` answers a window from its cache for 30 seconds whatever is written meanwhile (`LedgerCache`, [item 215](215-the-city-s-cost-breakdown-query-costs-3-6-percent.md)).
While a city waits for its history's first read, the scene rebuilds on every snapshot and reads the ledger's windows partway through the ingest, so when the read finishes and the city opens it shows that cached, partial window for up to 30 seconds.
Measured on [item 240](240-the-metropolis-demo-reads-as-a-light-user.md)'s heavy metropolis (about 9,565 messages): a 25-second recording opens on $10.85–$13.62 for the day and reaches $149.74–$191.64 by its last frame, while the store already held every message when `HeftsRead` turned true.
It misleads a live city after its first read as well as every still and clip filmed from a heavy history, where the frame is taken at the opening.

## The fix

When the history's first read finishes (the snapshot whose `HeftsRead` turns true, which is also what opens a capture), the scene has the ledger read its windows fresh instead of reusing a cached answer; the 30-second reuse stands for every snapshot after.
Tests: in `pkg/stats`, a window the scene asks to be read fresh is read again even inside its 30 seconds; in `pkg/city`, the scene that opens on a finished read shows each window as the store holds it.

## Answered while building

- **The test tree** (manager, 2026-10-24): approved as sent. `stats.Ledger.ReadFresh()` marks every cached window and the session costs due once, and `Scene.SetSnapshot` calls it when a snapshot's `HeftsRead` turns true after one that was not, for a capture and a live city alike. `TestALedgerReadsFreshWhenAsked` in `pkg/stats/ledger_test.go` and `TestTheSceneReadsTheLedgerFreshWhenItsHistoryIsRead` in `pkg/city`, including that a read snapshot after a read one does not read fresh again, so the 30 s reuse item 215 bought is kept.

## Closed

Fixed as answered above, in two botropolis commits: `fec9e4b` (r1010) adds `Ledger.ReadFresh`, with the session costs read fresh alongside the windows, and has the scene ask it when a read snapshot follows an unread one;
and `70348ca` (r1015) adds the changelog entry under Fixed.
`TestALedgerReadsFreshWhenAsked` (in its own file, `pkg/stats/ledger_fresh_test.go`, rather than `ledger_test.go`) and `TestTheSceneReadsTheLedgerFreshWhenItsHistoryIsRead` were red before the fix.
A frame showing it is item 240's re-filmed metropolis overview, whose day's spend should read whole at the opening; that still goes to Aria with item 240's.
