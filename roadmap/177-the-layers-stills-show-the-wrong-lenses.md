# 177. The demo's "Spend" and "Context pressure" stills show the Work and Cost lenses, and the website publishes them so

**Open. Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

`botropolis/demo/scenarios/layers.yaml` was written for the nine views.
Its stills press a digit and name what it used to show:

| shot | keys | titled | shows now |
| --- | --- | --- | --- |
| `spend` | `Digit2` | Spend, *"coloured by what each session has cost"* | the Work lens |
| `pressure` | `Digit3` | Context pressure, *"coloured by how full each session's context is"* | the Cost lens |

The six lenses are `city.Lenses` (`botropolis/pkg/city/lens.go`): Attention, Work, Cost, Capacity, Health, Connections.
The lens panel in each frame names the lens it shows, at (32, 76) in a 1920×1080 frame: *Work* in `layers/spend.png` and *Cost* in `layers/pressure.png`, both in `botropolis/dist/demo/` as filmed on 2026-10-19 and again by this audit.

![The lens panels of the two stills](../docs/references/177-the-layers-stills-show-the-wrong-lenses.png)

The website lists both under the old titles: `botropolis.city/src/data/media.json` carries `layers/pressure` as "Context pressure" and `layers/spend` as "Spend".
The `views` clip's description still promises nine views by their old names — *"attention, spend, context pressure, staleness, servers, traffic, models, fan-out and health"* — and it is in the website's theatre (`src/data/theater.ts`).

The fix renames and re-keys the stills (Cost is `Digit3`; Capacity, `Digit4`, is the nearest to context pressure), rewrites the clip's description for the six, refilms, and re-imports the website's media.
The scenario test already resolves every key name; it could also hold each still's title to the lens its digit selects, so a reshuffle of the lenses fails `make test` instead of the website.
