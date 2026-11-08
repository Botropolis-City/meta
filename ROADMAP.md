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
| [96](roadmap/096-the-global-shortcut-on-wayland.md) | the global shortcut on Wayland through the portal, with an app id and `.desktop` file | 245 | nobody, on a cloud VM |
| [164](roadmap/164-no-soak-test-for-the-growth-budget.md) | an 8-hour soak test for the growth budget, on a release checklist | 245 | nobody, the budget is set |
| [204](roadmap/204-the-ingest-could-run-in-a-child-process.md) | the ingest shares the daemon's process, so its CPU priority can't be lowered on macOS: run it as a child process | 200 | nobody |
| [212](roadmap/212-every-frame-re-records-every-drawable.md) | every frame re-records every drawable to find it unchanged: 43–59% of Draw; the way toward 10% of a core | — | nobody |
| [238](roadmap/238-a-baked-look-can-differ-by-a-pixel-for-some-shapes.md) | a baked look can still differ from the direct draw by a pixel for some shapes | — | nobody, until it shows on the art |
| [245](roadmap/245-test-machines-in-the-cloud.md) | cloud machines for the overnight soak and the Wayland desktops: Hetzner, plan-only | 266 | nobody, Aria chose |
| [256](roadmap/256-the-cache-tests-see-no-cache-hit-under-load.md) | the test-cache acceptance tests sometimes see no cache hit when the machine is busy | — | nobody, a flaky test |
| [257](roadmap/257-every-lamp-glow-splits-a-batch.md) | every lamp's glow splits the night batch: a glow layer of its own, then the bridge road's lamps back | 247 | nobody, the ceiling is set |
| [261](roadmap/261-past-four-seconds-the-metropolis-draws-over-its-ceilings.md) | past 4 s the metropolis draws over its draw ceilings (21 by day, 38 by night) | 260 | nobody, the ceilings are set |
| [262](roadmap/262-the-darwin-priority-test-can-hang-ci.md) | the macOS priority test can hang a CI job until it dies, silently | — | nobody, a flaky test |
| [265](roadmap/265-what-1-0-0-needs-is-not-written-down.md) | the bar a build must clear to be 1.0.0, drafted for Aria | — | Aria's, which criteria make the bar |
| [267](roadmap/267-the-website-s-version-is-typed-by-hand.md) | the site shows the latest release without a hand edit | — | nobody, Aria chose rebuilding on release |
| [277](roadmap/277-a-big-city-keeps-records-for-what-is-off-screen.md) | a big city keeps drawing records for what is off screen | — | nobody, parked until item 270 needs it |
| [296](roadmap/296-the-tray-on-macos.md) | the city has no menu-bar item on macOS | 293, 245 | nobody, Aria ruled the tray |
| [299](roadmap/299-version-check-trusts-whatever-is-in-bin.md) | `make version-check` fails a landing on binaries left in `bin/` from before a bump | — | nobody, a defect in a guard |
| [355](roadmap/355-the-landing-queue-s-slow-waiter-test-times-out-on-macos-intel.md) | the landing queue's slow-waiter test times out on the Intel macOS runner | — | nobody, a flaky test |
| [357](roadmap/357-make-land-s-own-tests-miss-the-wait-under-load.md) | `make land`'s own acceptance tests miss the wait under load | — | nobody, a flaky test |
| [358](roadmap/358-the-performance-gate-records-nothing-of-the-machine-s-power-state.md) | the performance gate records nothing of the machine's power state | — | nobody, a gap in the method |
| [335](roadmap/335-the-greedy-batcher-splits-on-which-draw-leads.md) | the frame's batcher is greedy, so the draw-command count depends on which source happens to lead | — | nobody, after 0.4.0 |
| [339](roadmap/339-the-stress-measures-follow-the-clock.md) | the stress city's measures follow the wall clock, so a night run does 3.5% more work than a day run | — | nobody, after 0.4.0 |
| [342](roadmap/342-the-release-session-runs-the-live-half-of-a2-a4-and-a6.md) | the release session runs A2, A4 and A6 headless, as live checks L3–L5 | — | nobody's |
| [360](roadmap/360-the-website-still-describes-the-city-of-0-3-0.md) | the website catches up with 0.5.0: groups, the clinic, the controls | — | nobody's |
| [363](roadmap/363-the-station-label-is-drawn-only-on-the-test-sheet.md) | the station label is drawn only on the render test sheet, so it is dead code | — | nobody's |
| [366](roadmap/366-release-0-5-1.md) | release 0.5.1: items 364, 365, 367 and 368 | 364, 365, 367, 368 | nobody's |
| [369](roadmap/369-make-publishable-refuses-forever-on-a-merged-pull-request.md) | `make publishable` refuses forever on a merged pull request's ref | — | nobody's |
| [370](roadmap/370-botropolis-city-has-no-publishable-guard.md) | botropolis.city has no `make publishable` guard | 369 | nobody's |
| [371](roadmap/371-the-demo-film-cannot-show-a-move-taking.md) | the demo film cannot show a move taking: a filmed city's moves go to a private state copy | — | nobody's |

## Waiting on Aria

- **What 1.0.0 needs**, [item 265](roadmap/265-what-1-0-0-needs-is-not-written-down.md): nine drafted criteria to keep, change or drop.
- **The validation checklist's six steps left to her**, A1–A6 in [`validation-checklist.md`](roadmap/validation-checklist.md): attach in a real terminal, `c` in a real district, a real notification and the away list, `!` in a real session, the waybar module, and `status --live`. Each says the keys to press and what she should see; everything else on it is scripted or run by an agent (item 246). They run against each release build.

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
