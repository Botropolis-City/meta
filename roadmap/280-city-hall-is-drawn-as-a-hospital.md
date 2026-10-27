# 280. City Hall is drawn as a hospital, and the hospital should stand for what needs Aria

**Done 2026-10-27 (`d6b2b27`, r1186). Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria ruled what the hospital becomes; its look is a frame for her.**

Depends on: nothing
Landed: slice 1 (`296cd0b`, r1169).
Landed: slice 2 (`ef66361`, r1175).
Landed: slice 3 (`6f672d8`, r1174).
Landed: slice 4 (`77ae413`, r1179).
Landed: slice 5 (`d6b2b27`, r1186).

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
- **The clinic is dark at night, for now** (manager, 2026-10-27, landing for 0.3.3's overnight soak): its lit windows took the metropolis demo's night frame to 38 draw commands against item 236's ceiling of 37, and unlit it measures 37 again.
  Raising the ceiling is Aria's call, so slices 1–3 landed with the clinic unlit at night (`ef66361`), a temporary departure from the lit frames she approved in `r1138-item-280-clinic.png`.
  Next: fold its lights into the hall's or library's batch within the ceiling, time-boxed to about an hour; if that fails, the manager puts the ceiling to Aria.
- **Folding the clinic's lights into another batch does not work** (session's measurement, 2026-10-27, about half an hour of the hour's time box).
  The night lights are laid in depth order, each lit building's panes one draw, after any earlier cut that meets them.
  Logged on the metropolis demo's night frame, lighting the clinic changes one place in that order: a punch cut, from a sprite behind the clinic whose box meets its panes, is laid before the clinic's warm draw and not with the next cut, and the clinic's draw follows it.
  The cuts cost the same either way, so the one command over the ceiling is the clinic's own window draw, and the cut it must follow is what keeps it from joining the hall's or library's warm draw, which are elsewhere in the order.
  Laying it earlier would let things behind it cut its lit windows, so the order is the picture, not batching.
  Lighting a fourth landmark at night therefore costs one draw command a frame by this design: Aria's choice is to raise item 236's night ceiling from 37 to 38, or keep the clinic dark at night.
- **Slice 4, the clinic's count at scale** (manager, 2026-10-27, from 0.3.3's release check): the 600-district fit frame came in at a 16.47 ms median against item 270's 16 ms bar, and a control put the regression in r1166–r1176.
  The standing key and the plate asked for the clinic's count every frame, and it built the whole list to count it, putting every building through the trouble test: the walk item 270 took out of triage.
  The city now lists what may be in trouble when it is indexed, and the count looks only at that and what needs you (`77ae413`, r1179), held to a walk over every building across the 24 h edge.
- **The clinic at night** (Aria, 2026-10-27): *"Raise to 38 and light it"*: item 236's night ceiling goes from 37 to 38 draw commands a frame, and the clinic is lit at night like the hall and the library, after 0.3.3.
- **The clinic lights at night** (Aria, 2026-10-27): she raised item 236's night ceiling from 37 to 38 draw commands, and the clinic's windows light as the library's and the hall's do (`d6b2b27`, r1186), so 0.3.3's dark clinic lasted one release.

## Done

City Hall is a stone hall modelled in the sprite pipeline, with a six-column portico, a pediment and a clock tower whose face shows from every heading, lettered on its frieze and lit at night (`296cd0b`).
The old hall's building-n, at 70% of its size, is the clinic in the plaza's fourth corner: its plate counts the sessions needing Aria plus those in trouble — an API error last, stopped mid-turn within a day though not interrupted, or three or more failed tools in a row — and a click or `a` opens the list, needing-you first in triage order, then trouble, most recent first, with `1`–`9` and the arrows to jump (`69fc896` to `ef66361`, `95e0988`).
The count is held to a walk over every building at scale (`77ae413`), and the clinic lights at night (`d6b2b27`).
Frames: `botropolis/docs/screenshots/r1138-item-280-hall.png`, `r1138-item-280-clinic.png` and `r1138-item-280-clinic-menu.png`, which Aria judged *"Good, land them."*
Tests: `pkg/city/clinic_test.go` (rows, order, count, reasons), `pkg/render/clinic_test.go` (click, `a`, keys), `TestClinicCountAtScale`, `TestTranscriptTailTrouble` and `TestTrouble`.
Budgets Aria moved for it: z1 resident 18 → 20 MiB, and the night draw-command ceiling 37 → 38; z1.5 stays at 40 MiB with its third page nearly full.
