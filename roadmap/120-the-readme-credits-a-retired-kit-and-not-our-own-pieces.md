# 120. The README credits a retired kit, and not the pieces drawn here

**Fixed 2026-10-18 (`80f3526`, r653). Filed 2026-10-18 (r628), from the art audit Aria asked for. Nobody's call — Aria asked for it.**

Aria, 2026-10-18: *"Make sure that for anything we pulled from an asset pack we have followed their licensing and attributed and thanked them."*

`botropolis/README.md:184`, under *Thanks*, says the city is drawn from Kenney's 3D kits and lists nine, including **the Space Kit**.
The Space Kit's rover was retired in item 89 (`design/sprite-pipeline.md:48`).
Nothing from it is in either atlas manifest, and `tools/fetch-kits` no longer fetches it.
`pkg/assets/kits/README.md`, the per-kit table, is already correct.

The same sentence says *the city* is drawn from the kits.
Since item 109, every session's building is the city's own, modelled from primitives in `tools/render-sprites/buildings.py`.
So are the drone, the fountain, the skips, the trucks and the ruins: 95 of the 155 sprites in `pkg/assets/kits/kits-z1.json` are under `botropolis/`.
The credit should say which is which, so Kenney is thanked for what is Kenney's and not for what is not.

`design/open-questions.md:32` also names the Space Kit, but as the record of what was settled on 2026-09-18, so it stays as written.

## The fix

Drop the Space Kit from the README's list.
Say that the roads, trees, vehicles, boats and landmarks are Kenney's, and that the session buildings, drone, fountain and site vehicles are modelled in `tools/render-sprites` in the kits' palette.
Keep the thank-you and the donate link.

## Done when

The README's kit list matches `tools/fetch-kits`'s defaults, and it says which pieces are drawn here.

## Closed

Fixed in two commits, `97e9e66` (r652) and `80f3526` (r653).
The README's thanks now name the eight kits `tools/fetch-kits` fetches, each by its full name, and no Space Kit.
It says the roads, trees, cars, trains, boats and landmarks are Kenney's,
and that every session's building, the drone, the fountain and the building sites are modelled in `tools/render-sprites`.
The thank-you and the donate link stay.
`testing/acceptance/credits_test.go` holds it there: it fails if the thanks miss a default kit, name one the pipeline does not fetch, or stop naming `buildings.py`.

Two additions came from the manager during the work.
The test also pins Inter's credit under the SIL Open Font License,
and, on Aria's ruling of 2026-10-18, Inter is credited to its licence holder, The Inter Project Authors, rather than its designer.
JetBrains Mono was proposed for the README too, but it is only the website's font and nothing in the app embeds it, so the website credits it and the README does not.
The asset inventory sent to the manager, read from both atlas manifests, is the shared source for the credits in items 119 and 122.
