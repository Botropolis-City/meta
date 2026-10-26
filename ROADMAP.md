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
| [255](roadmap/255-a-roads-vehicle-says-what-kind-of-traffic-it-is.md) | a road's vehicle says its traffic: car, van, box truck, motorbike; no message rides a group's line | — | nobody, Aria decided |
| [256](roadmap/256-the-cache-tests-see-no-cache-hit-under-load.md) | the test-cache acceptance tests sometimes see no cache hit when the machine is busy | — | nobody, a flaky test |
| [257](roadmap/257-every-lamp-glow-splits-a-batch.md) | every lamp's glow splits the night batch: a glow layer of its own, then the bridge road's lamps back | 247 | nobody, the ceiling is set |
| [259](roadmap/259-a-long-boat-straddling-a-raised-deck-is-drawn-in-one-piece.md) | a long boat straddling a raised deck is drawn all in front of it or all behind | 252 | nobody, a defect |
| [261](roadmap/261-past-four-seconds-the-metropolis-draws-over-its-ceilings.md) | past 4 s the metropolis draws over its draw ceilings (21 by day, 38 by night) | 260 | nobody, the ceilings are set |
| [262](roadmap/262-the-darwin-priority-test-can-hang-ci.md) | the macOS priority test can hang a CI job until it dies, silently | — | nobody, a flaky test |
| [265](roadmap/265-what-1-0-0-needs-is-not-written-down.md) | the bar a build must clear to be 1.0.0, drafted for Aria | — | Aria's, which criteria make the bar |
| [267](roadmap/267-the-website-s-version-is-typed-by-hand.md) | the site shows the latest release without a hand edit | — | nobody, Aria chose rebuilding on release |
| [268](roadmap/268-a-first-sighting-shown-only-behind-a-panel-is-spent.md) | a first sighting shown only behind a covering panel is spent and never shows | — | nobody, a defect |
| [269](roadmap/269-make-publishable-fails-in-a-worktree-once-main-moves.md) | `make publishable` fails in a worktree once github's main moves | — | nobody, a defect in a guard |
| [270](roadmap/270-the-city-freezes-with-hundreds-of-districts.md) | the city freezes with hundreds of districts and groups of hundreds | — | nobody, a defect |
| [273](roadmap/273-scripted-runs-are-drawn-as-full-buildings.md) | scripted runs hidden by default, shown as a cart or stand | — | nobody, Aria ruled; the stall is a frame for her |
| [277](roadmap/277-a-big-city-keeps-records-for-what-is-off-screen.md) | a big city keeps drawing records for what is off screen | — | nobody, parked until item 270 needs it |
| [278](roadmap/278-packing-a-session-does-not-take-it-to-the-depot.md) | packing a session leaves it boarded up instead of taking it to the depot | — | nobody, a defect |
| [279](roadmap/279-the-map-pans-only-with-the-left-button.md) | the map pans only with the left button; right and middle drags pan too | — | nobody, Aria asked |
| [280](roadmap/280-city-hall-is-drawn-as-a-hospital.md) | City Hall gets a hall; the hospital becomes the clinic for what needs Aria and errors | — | nobody, Aria ruled; frames for her |
| [281](roadmap/281-a-group-line-can-lead-nowhere.md) | a group's line can stand alone with one station and lead nowhere | — | nobody, a defect |
| [282](roadmap/282-the-wheel-cannot-reach-skyline-or-zoom-the-plan.md) | the wheel cannot always reach Skyline, and the City Plan cannot be zoomed | — | nobody, Aria said what she wants |
| [283](roadmap/283-districts-can-be-moved-only-one-at-a-time.md) | several districts can be selected and moved together | — | nobody, Aria asked |
| [284](roadmap/284-copying-a-path-freezes-the-city-with-xclip.md) | copying a path freezes the whole city when the clipboard tool is xclip | — | nobody, a defect |
| [285](roadmap/285-a-tied-temporary-session-s-spend-counts-under-temporary.md) | a tied temporary-directory session still counts its spend under Temporary | — | nobody, a defect |
| [286](roadmap/286-claude-actions-run-on-the-city-s-own-loop.md) | Resume, New, Stop and the other claude actions wait on the city's own loop | — | nobody, a defect |
| [287](roadmap/287-a-card-changes-size-as-the-pointer-moves-over-its-buttons.md) | a session's card changes size as the pointer moves over its buttons | — | nobody, Aria said what she wants |
| [288](roadmap/288-there-is-no-obvious-way-to-make-a-new-group.md) | there is no obvious way to make a new group, and move to group offers none | — | nobody, Aria said what she wants |
| [289](roadmap/289-the-new-session-panel-ignores-typing.md) | the New session panel takes no typed text, only scripted keys | — | nobody, a defect |

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
