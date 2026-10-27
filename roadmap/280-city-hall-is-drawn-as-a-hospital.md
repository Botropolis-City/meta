# 280. City Hall is drawn as a hospital, and the hospital should stand for what needs Aria

**Open, in progress since 2026-10-26 in the session "item 280". Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria ruled what the hospital becomes; its look is a frame for her.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: *"city hall is a hospital. I haven't noticed that before because I haven't seen this side. We should swap that with another building. We should also reuse the hospital for something else because I like it. Maybe something like errors or a quick menu of what sessions need me right now?"*
Asked which, she chose **both**: one building for what needs her now, and errors.

The hall's sprite is Kenney's `city-kit-commercial/building-n` (`pkg/render/recipes.go`; `tools/render-sprites/render.py`), whose green cross the pipeline itself calls *City Hall's green cross*: a clinic's sign.

## The fix

1. **City Hall** gets a building that reads as a town hall from every heading — a civic front, columns or a clock — from the kits or modelled from primitives as the ruins and stalls are, with its panes, walls, label anchor and lights re-measured (`pkg/assets/landmarkpanes_test.go`, `pkg/render/landmark*_test.go`).
2. **The hospital** becomes a landmark of its own, the city's clinic: its count shows how many sessions need Aria now plus how many are in trouble (API errors, failed tools, crashes), and clicking it opens a **quick menu**: every session waiting on her first, then the troubled ones, each with its reason and a key to jump to it.
3. Frames for Aria: the new hall and the clinic, from each heading, by day and night, and the menu open.
4. Tests: the menu lists exactly the needs-you sessions, then the troubled ones, in that order; a key jumps to each; the count matches.

## Answered while building

- **The design** (session's, approved by the manager, 2026-10-26): the hall is modelled from primitives, a stone block with a six-column portico, pediment and a clock tower; the hospital sprite becomes the clinic on the plaza's free corner. Its count is the sessions that need Aria, exactly the triage walk, plus those in trouble, each counted once; *in trouble* is an API error on the last record in slice 2, and a crash mid-turn or three failed tools in a row in slice 3. The quick menu lists needs-you in triage order, then trouble, newest first, with 1–9 and arrows to jump; key `a` if it is free everywhere.
- **The z1.5 atlas is full** (session's measurements, 2026-10-26; Aria's ruling): with the new hall, the clinic at 70% of the old hospital's size and item 273's stalls, page three of z1.5 packs 1,015 of 1,024 rows within the 40 MiB budget; trimming margins, other packing orders and smaller clinics bought nothing more. Aria, asked what the next sprite at that zoom does: decide case by case, the item first making room and bringing her the choice with numbers, the budget staying 40 MiB until she rules.
- **Aria's verdicts** (2026-10-26): the hall and the clinic frames, *"Good, land them"*; and the normal-zoom resident budget, which could hold the hall or item 273's enlarged stalls but not both, rises from 18 to 20 MiB, about 190 rows then free, rather than shrinking either.
