# Botropolis — roadmap

The plan and its current state.
Every numbered item has its own file in [`roadmap/`](roadmap/); this file is the index and nothing else.

Detail belongs in `roadmap/`, rules and what-exists belong in [DESIGN.md](botropolis/DESIGN.md), and neither belongs here.
This file grew to 2,689 lines by holding both, which is what it is being kept short to avoid.

The roadmap moved here from the botropolis repository on 2026-10-15, at botropolis r410 (`d6ac05f`).
Its history before that is in that repository: `git log -- ROADMAP.md roadmap/` there.
Revisions cited in items (`r<N>`) still count botropolis's commits.

## Phases

| phase | what | state |
| --- | --- | --- |
| 7 | UI foundation | shipped 2026-09-18 |
| 8 | City plan | shipped 2026-09-18 |
| 9 | Art pipeline and art pass | shipped 2026-09-18 |
| 10 | Parity with bot-crossing | shipped 2026-09-18 |
| 11 | Info and control | shipped 2026-09-18 |
| 12 | Packaging and polish | shipped 2026-09-18 |
| 13–18 | audit follow-up | done, [`audit-r96.md`](roadmap/audit-r96.md) |
| 19 | Info views | done, [`phase-19-info-views.md`](roadmap/phase-19-info-views.md) |
| 20 | The map has to explain itself | one item open, [`phase-20-explain-itself.md`](roadmap/phase-20-explain-itself.md) |
| 21 | The art batch | done, items 35–68 |

Phases 7–12 were specified in [`phases-7-12.md`](roadmap/phases-7-12.md) and audited at r96.

## Open

| item | what it wants | depends on | whose call |
| --- | --- | --- | --- |
| [95](roadmap/095-the-global-shortcut-on-macos.md) | the global shortcut on macOS: registering is solved, coming forward needs a Mac run | — | nobody, a GitHub-hosted macOS runner first |
| [96](roadmap/096-the-global-shortcut-on-wayland.md) | the global shortcut on Wayland through the portal, with an app id and `.desktop` file | 245 | nobody, on a cloud VM |
| [105](roadmap/105-the-demo-cannot-record-or-stage-an-agent-team.md) | the demo cannot record or stage an agent team, so team messages cannot be filmed | 89 (slice 5) | nobody |
| [164](roadmap/164-no-soak-test-for-the-growth-budget.md) | an 8-hour soak test for the growth budget, on a release checklist | 245 | nobody, the budget is set |
| [190](roadmap/190-a-statistics-store-that-will-not-open-turns-statistics-off-silently.md) | a statistics store that will not open turns statistics off with no log, doctor row or notice | — | nobody, a defect |
| [204](roadmap/204-the-ingest-could-run-in-a-child-process.md) | the ingest shares the daemon's process, so its CPU priority can't be lowered on macOS: run it as a child process | 200 | nobody |
| [212](roadmap/212-every-frame-re-records-every-drawable.md) | every frame re-records every drawable to find it unchanged: 43–59% of Draw; the way toward 10% of a core | — | nobody |
| [213](roadmap/213-the-2000-session-daemon-is-over-its-cpu-budget.md) | a settled daemon on a 2,000-session home is just over its CPU budget: 2.3–2.6% counted against 2% | — | nobody |
| [214](roadmap/214-the-dashboards-layout-sits-at-its-budget.md) | the unfocused dashboard's layout sits at its 1% budget once kernel time counts: 1.04% | — | nobody |
| [220](roadmap/220-a-large-island-gets-a-second-bridge.md) | a large island gets a second bridge | 218 | nobody, Aria set the threshold |
| [238](roadmap/238-a-baked-look-can-differ-by-a-pixel-for-some-shapes.md) | a baked look can still differ from the direct draw by a pixel for some shapes | — | nobody, until it shows on the art |
| [245](roadmap/245-test-machines-in-the-cloud.md) | cloud machines for the overnight soak and the Wayland desktops: Hetzner, plan-only | — | nobody, Aria chose; waits on her account |
| [246](roadmap/246-the-validation-checklist-predates-0-3-0.md) | the validation checklist rewritten against 0.3.0, scripted where it can be | — | nobody |
| [247](roadmap/247-no-road-leads-to-a-bridge.md) | no road leads to a bridge: its ramp comes down onto grass | 220 | nobody, a defect |
| [248](roadmap/248-a-synthetic-history-cannot-be-made-outside-go-test.md) | `botropolis-demo synth-home`: a synthetic history of real size outside `go test`, for item 245's soak | — | nobody |
| [249](roadmap/249-captures-fail-under-load-at-the-30-second-open-ceiling.md) | acceptance captures fail under load at the 30 s open ceiling | — | nobody, a defect |
| [250](roadmap/250-a-session-running-a-background-command-says-it-needs-you.md) | a session whose turn ended over a running background command shows needs-you | — | nobody, a defect |
| [251](roadmap/251-a-killed-headless-city-leaves-its-xvfb-running.md) | a killed headless city leaves its Xvfb running: 83 orphans, 8.9 GiB | — | nobody, a defect |
| [252](roadmap/252-the-second-bridge-is-too-low-for-the-liner.md) | the second bridge's deck is too low for the liner: raise it over the river | 220 | nobody, Aria chose |

## Waiting on Aria

- **A Hetzner account for the test machines** (item 245): create it, put the Cloud token and the Robot user and password in 1Password, and set their three references in the git-ignored `testing/machines/.env`; item 245 then runs its plan for her to read, and items 164 and 96 wait on it.
- **The validation checklist** has its own file, [`validation-checklist.md`](roadmap/validation-checklist.md). **Steps 1 and 8 pass** — step 1 now reconciles by session id rather than by title, which is what item 71 bought. **The other eight need her hands on the keyboard**, and the file says which keys.

The nine unadjudicated entries were read one by one on 2026-09-29 and all nine are now closed: item 24 by Aria's ruling that the six undrawn pieces are a deliberate reserve, and items 22, 23, 26, 27, 28, 29, 31 and 33 by adjudication, each with the reason on its own file.
**It was worth doing.** Two facts had been measured five times between them and owned by nothing — the 10% bar being missed, and the atlas start-up peak holding two copies of every page with its fix named and deferred nine phases ago.
Closing those eight without reading them would have retired both silently, which is exactly what the list was there to prevent.

## Background

Written when this roadmap was opened and still the frame for it.

- [why-a-second-pass.md](roadmap/why-a-second-pass.md) — the r64 frame this plan was opened against
- [design-brief.md](roadmap/design-brief.md) — what "modern and intentional" means here
- [art-direction.md](roadmap/art-direction.md) — the kits, and why these ones
- [parity-with-bot-crossing.md](roadmap/parity-with-bot-crossing.md) — what the predecessor had, row by row
- [later.md](roadmap/later.md) — noticed while building, not in a phase; each one a question rather than a plan

## Not doing

Planets, orbit mode, a 3D renderer, network serving, quality presets beyond render scale and reduced motion, animated faces.
Each is either bot-crossing's setting rather than a feature, or a cost the footprint principle rules out.

## Where things are

| | |
| --- | --- |
| `roadmap/NNN-*.md` | one file per numbered item, 1–68 |
| `roadmap/phase-*.md` | the phases that carry their own sub-items |
| `docs/references/` | annotated crops from investigations, belonging to items |
| `botropolis/docs/screenshots/` | frames, cited by revision |
| [DESIGN.md](botropolis/DESIGN.md) | what exists, and the rules the work is held to |

Items are numbered in one series, 1–68.
Section 8's bugs 1–34 and the art batch's 35–68 continue the same numbering; phases 19 and 20 have their own small series, cited as "phase 20 item 3".
There are two bug 18s — road tiles, and rovers parking — both fixed, both left renumbered as written, because a dated record that gets tidied stops being a record.
Nothing cites either by number.

## Status, 2026-09-29

72 items, 68 closed, 4 open, 0 unadjudicated — counted by number.
By *file* it is 69 closed of 73, because the two bug 18s are one number and two entries.
Both figures are the same fact; this line quotes the first.
Gate green: `go build`, `go vet`, 22 test packages, `make lint` 0 issues.
The inventory is [`inventory-2026-09-29.md`](roadmap/inventory-2026-09-29.md).
