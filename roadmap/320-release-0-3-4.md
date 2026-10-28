# 320. Release 0.3.4

**Open. Filed 2026-10-28 (r1204) at Aria's request. Nobody's call — Aria set what it waits for and what it runs.**

Depends on: 319

Aria, 2026-10-28: *"let's plan and work towards 0.3.4 so we can release it asap. Sound like we just need 318, 319, a soak, a refilm, and then my checklist after that."*

## What it holds

Everything on `main` once item 315 has landed its last slice (item 318 turned out to be llvmpipe's growth, not the city's, so the release no longer waits on it): the tray (293), `c` attaching in the session's folder (302), the `light` setting (308, slice 1), the clinic's night windows (280), the truck at road speed (304), a recording city that opens on a big history (311), the opening's cost (315), and item 212's slices to that point.
Item 212 lands what is in flight by then; whatever is not landed then waits for 0.3.5.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) in full, as 0.3.3 did:

1. The candidate: `VERSION` 0.3.4 and its changelog section, landed with `make land`; from that commit until the tag nothing else lands, so the soak, the film and the checklist all measure one build.
2. The soak, on the candidate, pinned to night (item 308), after item 319 so a failed pre-flight explains itself; it must pass the 1 MiB an hour budget, as the first 0.3.4 soak is the first to give a verdict at all (item 164).
3. The re-film, once, on the candidate, in parallel with the soak; Aria judges the sheets.
4. The validation checklist's scripted steps, then Aria's A1–A7 on the candidate package, A7 being the tray round trip (item 293).
5. The release workflow, `dry_run` first; the AUR packages; the website's media, purging the media host's cache after the upload (item 307).
