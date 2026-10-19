# 147. A train's engine says its model's context window, and the engine wants another look

**Open, in progress since 2026-10-19 in the session "item 147". Filed 2026-10-19 (r748) at Aria's request, from item 134's frames. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`1a739df`, r749).

Each train on the loop is one model, and its wagons count that model's spend today ([item 78](078-trains-belong-on-the-main-view.md), [item 134](134-the-train-is-a-third-the-size-of-the-cars.md), item 116's cost wagons).
Aria, 2026-10-19, reviewing item 134's frames: models allow very different context windows (a million tokens against a few hundred thousand, and less), and the train should say so. Chosen among options: **the engine's class follows the model's window**, with wagons still counting spend. And: *"I don't love the train engine (front), is there a different sprite option?"*

## The fix

1. **Options first:** render every locomotive the Train Kit offers (and any other licensed pack's, per `botropolis/design/art-sources.md`) side by side at map scale beside a wagon and a car, for Aria to pick the engines; nothing is built before she picks.
2. **Engine class by window:** a small number of window classes (say up to 200k, up to 1M, over 1M — set from the models Claude Code reports), each with its own engine from the picked set, so the class reads at a glance; the window comes from what the transcript or the model table records, never guessed — a model whose window is unknown gets the default engine and its card says so.
3. The train's card names the model's window beside its spend.

Tests: each window class gets its engine; an unknown window gets the default and the card says unknown; the wagon count is unchanged by the engine; frames for Aria.
