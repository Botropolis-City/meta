# 78. Trains belong on the main view, as the cars do

**Done 2026-10-19 (`0b8f0b4`, r674). Filed 2026-10-10 (r377) at Aria's request: the trains that run round the outside should always be visible, like the cars. Nobody's call — she has asked for it, and the change is small.**

Bug 48 put the cars on the main view by adding `NetworkTraffic` to `ViewAttention` in `shown` (`pkg/city/network.go`).
The freight loop never got the same treatment: `NetworkFreight` is drawn only by `ViewSpend`, so on the view the city opens in, the trains are missing.
The track is not gated — `isoRails` draws it unconditionally (`pkg/render/iso.go`) — so the main view shows a railway round every district with nothing running on it.
The demo frames show exactly that: every metropolis, workshop and workday still has the loop and no trains.

**The change:** `ViewAttention: {NetworkTraffic, NetworkFreight}`.
The gate in `freight()` already reads `shown`, so nothing else moves.

What has to change with it:
- `pkg/city/network_test.go` asserts that the attention view shows no network but traffic; it has to name freight as the second exception, or it fails as it should.
- The comment over `trafficCars` and `freight` in `pkg/render/iso.go` says "Attention pays for neither", which has been wrong since bug 48 and would be wrong twice.
- Bug 48's reasoning carries over and should be recorded the same way: the info-view model is subtractive on purpose, and a train on the base view is motion the view does not explain. It is safe for the same reason the car is — a train's card names its model, its tokens, the unit a wagon stands for and the cost.
- A day with no tokens has no trains at all (`trains()` returns nothing for an empty breakdown). **Aria, 2026-10-10: "always visible means only when there is spend to show."** So no change there: the main view runs the trains whenever the Spend view would, and an idle day's loop stays empty.
- Cost: the carriages join the depth-sorted list on the main view, which is the view the CPU bar (item 69) is measured on.

## Done

`0b8f0b4` (r674) put `NetworkFreight` in `ViewAttention`, beside the cars and the drones, so the trains run on the main view whenever the Cost lens would run them, and an idle day's loop stays empty.
`TestNetworksPerView` gained "it should draw the freight, which explains itself on hover", red before the change, and freight became the third exception to the quiet-view check.
The comments in `network.go`, its test and `iso.go` that said Attention draws no network, or neither mover, are corrected, and `design/info-views.md` lists the train.
The acceptance tests' step budgets passed with the carriages in the main view's sorted list.

The frame is `botropolis/docs/screenshots/r674-item-78-train-hovered.png` (`ddec099`, r677): the workday demo on the main view, with the hovered train's card naming its model, its tokens, one wagon per 200k tokens and the cost.
Aria passed it on 2026-10-19: "pass the train as is".
The changelog entry landed in `eef124e`.
Her follow-up, the road off the island crossing the rail into the water, is a new item, not this one.
