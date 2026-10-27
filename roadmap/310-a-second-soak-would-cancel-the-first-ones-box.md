# 310. A second soak started beside the first would cancel the wrong box

**Open, in progress since 2026-10-27 in the session "item 310". Filed 2026-10-27 (r1194), found by the performance manager before ordering 0.3.3's second soak. Nobody's call — a defect.**

The soak runner (`testing/machines/machines`) keeps one record, `~/.local/state/botropolis-machines/soak.json`.
`apply` overwrites it without checking for a box already recorded, and `destroy` cancels whichever server it names when called, which a running soak's runner does when its soak ends.
So a second order while a soak runs replaces the first box's record: the first runner then cancels the second box mid-soak, and the first box bills until its booked cancellation.

## The fix

1. One record per run (`soak-<run id>.json`, or keyed by server), and every `destroy`, `diagnose` and `status` acts on its own run's record, never "the" record.
2. `apply` refuses, naming the box, when a record it would overwrite names a server that is still live.
3. Tests, on the fake transport: two runs started one after the other each cancel only their own server; a second apply over a live record refuses; an old single `soak.json` from before the change is still found and cancelled by the run that wrote it.
