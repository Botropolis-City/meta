# 310. A second soak started beside the first would cancel the wrong box

**Fixed 2026-10-27 (`7d97274`, r1153 of meta). Filed 2026-10-27 (r1194), found by the performance manager before ordering 0.3.3's second soak. Nobody's call — a defect.**

The soak runner (`testing/machines/machines`) keeps one record, `~/.local/state/botropolis-machines/soak.json`.
`apply` overwrites it without checking for a box already recorded, and `destroy` cancels whichever server it names when called, which a running soak's runner does when its soak ends.
So a second order while a soak runs replaces the first box's record: the first runner then cancels the second box mid-soak, and the first box bills until its booked cancellation.

## The fix

1. One record per run (`soak-<run id>.json`, or keyed by server), and every `destroy`, `diagnose` and `status` acts on its own run's record, never "the" record.
2. `apply` refuses, naming the box, when a record it would overwrite names a server that is still live.
3. Tests, on the fake transport: two runs started one after the other each cancel only their own server; a second apply over a live record refuses; an old single `soak.json` from before the change is still found and cancelled by the run that wrote it.

## Fixed

`7d97274` (r1153 of meta):

- Each soak order keeps its own record, `soak-<listing>.json`.
  It is keyed by the auction listing rather than the transaction, because the listing is known before the order, so `apply` can check it before spending anything; a bought listing leaves the auction.
- A run's destroy, its keep-on-failure and the cancel after a failed booking act on the run's own record only, and a run that orders nothing cancels nothing.
  That last one was not in the item: `run soak` always destroys in its `finally`, so a destroy that picked "the only record" would have cancelled another run's box whenever `apply` refused.
- `apply` refuses with exit 3, ordering nothing, to replace a record whose server Robot still lists, or one still on order.
- A `soak.json` from before the change is never written or moved, so the runner that wrote it, already loaded, still cancels its own box; `make destroy` finds it like any other record.
- `make destroy MACHINE=soak` cancels the only record, refuses and lists them when there are several, and takes `SERVER=N` to pick one.
- The fake Hetzner gives each order its own transaction and server.

Tests, on the fake transport: two runs side by side each cancel only their own server; `apply` and `run` over a live record refuse and cancel nothing; a record still on order refuses; a record whose server is gone is replaced; an old `soak.json` beside a new run is left as it was; `destroy` with only an old `soak.json`, with two records, with a named one and with a name no record holds.

Checking `--server` red found that argparse took it as an abbreviation of `--server-type`, so the old runner accepted it silently; the test names the record the old code would not have cancelled.

The main checkout runs the old code until someone pulls in it, and a second soak started from there would still overwrite `soak.json`.
