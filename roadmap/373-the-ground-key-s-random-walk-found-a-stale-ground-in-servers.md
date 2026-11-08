# 373. The ground key's random walk found a stale ground in the Servers lens

**Open. Filed 2026-11-08 (r1345), from item 355's `make land`. Nobody's call — a defect or a flaky test, not yet known which.**

`pkg/render` `TestTheGroundKey`, *"when the pointer, the view and the selection wander at random"*, failed with seed `1794114594191552824`: *"step 119: the kept ground is stale in view servers"* (`groundkey_test.go`, lines 492 and 498).
It failed inside `make land` for item 355, whose change touches only `tools/land-queue`, so it was already on `main` (`4aa474ce`).

## Where it stands

The walk takes its seed from the clock (`groundkey_test.go`, line 351) and logs it, but nothing can feed a logged seed back in, so the failing walk cannot be replayed.
This walk found real defects before ([item 347](347-a-pointed-at-tower-does-not-light-its-beams-and-beams-reach-the-depot.md) and [item 359](359-pointing-at-a-grouped-building-lights-only-that-building.md)), so treat it as a defect until it is shown otherwise.

## The fix

Let an environment variable set the walk's seed, run seed `1794114594191552824`, and see which move at step 119 leaves the Servers lens's kept ground stale.
Fix the cause in the ground key's invalidation, and add that move as a fixed case beside the walk.
