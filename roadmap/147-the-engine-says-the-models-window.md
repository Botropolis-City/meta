# 147. A train's engine says its model's context window, and the engine wants another look

**Done 2026-10-19 (`58076c8`, r756). Filed 2026-10-19 (r748) at Aria's request, from item 134's frames. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`1a739df`, r749).
Landed: slice 2 (`f50fbc5`, r754).
Landed: slice 3 (`58076c8`, r756).

Each train on the loop is one model, and its wagons count that model's spend today ([item 78](078-trains-belong-on-the-main-view.md), [item 134](134-the-train-is-a-third-the-size-of-the-cars.md), item 116's cost wagons).
Aria, 2026-10-19, reviewing item 134's frames: models allow very different context windows (a million tokens against a few hundred thousand, and less), and the train should say so. Chosen among options: **the engine's class follows the model's window**, with wagons still counting spend. And: *"I don't love the train engine (front), is there a different sprite option?"*

## The fix

1. **Options first:** render every locomotive the Train Kit offers (and any other licensed pack's, per `botropolis/design/art-sources.md`) side by side at map scale beside a wagon and a car, for Aria to pick the engines; nothing is built before she picks.
2. **Engine class by window:** a small number of window classes (say up to 200k, up to 1M, over 1M — set from the models Claude Code reports), each with its own engine from the picked set, so the class reads at a glance; the window comes from what the transcript or the model table records, never guessed — a model whose window is unknown gets the default engine and its card says so.
3. The train's card names the model's window beside its spend.

Tests: each window class gets its engine; an unknown window gets the default and the card says unknown; the wagon count is unchanged by the engine; frames for Aria.

## Decided

- **Where the window comes from** (the manager, 2026-10-19): the largest window any session on the model knew in the train's period, then the model table's, then unknown; the card says which.
  The store records a model without the `[1m]` suffix a session's model can carry, so the suffix is dropped to match them.
- **The class picks the engine and the hue colours the wagons** (the manager, 2026-10-19), so two models in one class share an engine and are told apart by their wagons and their cards.
- **The engines** (Aria, 2026-10-19, from `botropolis/docs/screenshots/r749-item-147-engine-options-both-sides.png`): up to 200k, `train-diesel-c`; up to 1M, `train-electric-bullet-a`; over 1M, `train-electric-double-a`; an unknown window, `train-locomotive-a`.
  The atlas carries these four and drops the diesels nothing draws, and every engine runs nose first.

## Done

In three slices.
The options sheet (`1a739df`, r749), all 29 engines in the Train Kit coupled nose first to a wagon at map scale, and again from both sides (`9a98417`, r753), from which Aria picked.
The window (`f50fbc5`, r754): a train's window is the largest any session on its model knew in the last 24 h, then the model table's, then unknown, and the card's second line names it and where it was read; a session now says whether its window is known (`Session.ContextKnown`), which it did not, so an unknown model read as 200k. `TestTrainWindow` (`botropolis/pkg/city/city_test.go`) holds it, and dropping the period check or the `[1m]` trim each turn three red.
The engines (`58076c8`, r756): each class runs behind its picked engine, the hue colours only the wagons, and the atlas carries the four and drops `diesel-a` and `diesel-b`. `TestEngineByWindow` holds the class to its engine and the wagon count to the spend; `TestVehicleScale` holds the four engines to item 134's width band.
The frames are `botropolis/docs/screenshots/r754-item-147-engine-200k.png`, `-1m`, `-over-1m` and `-unknown` (`8944ff4`, r757), the workday demo with the dearest train hovered. Aria approved them on 2026-10-19.
The changelog entries are `e1fc580`.

**For Aria, beyond what was filed:**

- **Trains ran backwards on every stretch of track along x**, which the old diesels hid by looking the same from either end.
  The atlas now records where each train piece's nose lands in its sprite, and `TestEngineRunsNoseFirst` drives every engine round the loop at all four headings against it; putting the old turn back turns it red for all four.
  Trains turn by their own `trainTurn`; the cars share the fault in `carTurn` and are their own item.
- **Over 1M cannot show yet.** Trains come only from Claude Code's own transcripts, whose window tops out at 1M, and a Claude model with no session that knows its window reads 200k from the model table rather than unknown.
  The over-1M and unknown frames, and the 1M one, set every train's window with a staging hook that was not committed, as item 132's frames did; the 200k frame is the demo as it stands.
