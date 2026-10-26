# 280. City Hall is drawn as a hospital, and the hospital should stand for what needs Aria

**Open. Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria ruled what the hospital becomes; its look is a frame for her.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: *"city hall is a hospital. I haven't noticed that before because I haven't seen this side. We should swap that with another building. We should also reuse the hospital for something else because I like it. Maybe something like errors or a quick menu of what sessions need me right now?"*
Asked which, she chose **both**: one building for what needs her now, and errors.

The hall's sprite is Kenney's `city-kit-commercial/building-n` (`pkg/render/recipes.go`; `tools/render-sprites/render.py`), whose green cross the pipeline itself calls *City Hall's green cross*: a clinic's sign.

## The fix

1. **City Hall** gets a building that reads as a town hall from every heading — a civic front, columns or a clock — from the kits or modelled from primitives as the ruins and stalls are, with its panes, walls, label anchor and lights re-measured (`pkg/assets/landmarkpanes_test.go`, `pkg/render/landmark*_test.go`).
2. **The hospital** becomes a landmark of its own, the city's clinic: its count shows how many sessions need Aria now plus how many are in trouble (API errors, failed tools, crashes), and clicking it opens a **quick menu**: every session waiting on her first, then the troubled ones, each with its reason and a key to jump to it.
3. Frames for Aria: the new hall and the clinic, from each heading, by day and night, and the menu open.
4. Tests: the menu lists exactly the needs-you sessions, then the troubled ones, in that order; a key jumps to each; the count matches.
