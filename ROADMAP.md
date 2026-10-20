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
| [69](roadmap/069-the-10-percent-cpu-bar-is-missed.md) | the 10% CPU bar: still the bar, or the wrong number for a busy city? | — | Aria |
| [66](roadmap/066-115-mb-private-dirty-curiosity.md) | ~115 MB of private dirty unaccounted for, filed as a curiosity | — | nobody, until it costs something |
| [76](roadmap/076-what-the-website-still-needs-filmed.md) | the website's stand-ins: a hero loop, a still per view, a social card, chosen posters, anchors | — | nobody, filming work |
| [95](roadmap/095-the-global-shortcut-on-macos.md) | the global shortcut on macOS: registering is solved, coming forward needs a Mac run | — | nobody, needs a Mac |
| [96](roadmap/096-the-global-shortcut-on-wayland.md) | the global shortcut on Wayland through the portal, with an app id and `.desktop` file | — | nobody, needs GNOME or KDE |
| [105](roadmap/105-the-demo-cannot-record-or-stage-an-agent-team.md) | the demo cannot record or stage an agent team, so team messages cannot be filmed | 89 (slice 5) | nobody |
| [149](roadmap/149-what-1-0-0-promises.md) | what 1.0.0 promises: the surface written down, golden tests, and a layout file that is never reset in silence | — | nobody |
| [154](roadmap/154-a-fresh-eyes-audit-of-the-city.md) | a fresh-eyes audit of every scene, panel and mode, filing each small defect as its own item; no performance | — | nobody, the audit finds |
| [156](roadmap/156-the-city-s-go-heap-reaches-gigabytes-at-start-up.md) | the city's Go heap reaches gigabytes in its first seconds and keeps them; bisect r409..r745 | — | nobody, a defect to diagnose |
| [157](roadmap/157-the-daemon-s-heap-cap-keeps-it-collecting.md) | the daemon's 16 MiB heap cap and per-rescan release keep its collector running | — | nobody |
| [158](roadmap/158-group-detection-reruns-pairwise-on-every-prompt.md) | group detection re-runs pairwise on every prompt in any session | — | nobody |
| [159](roadmap/159-first-launch-takes-the-machine.md) | first launch: ≤ 1 core, ≤ 256 MiB, resumable, a map in 5 s, real progress | 157 | nobody, the budget is set |
| [160](roadmap/160-the-usage-probe-starts-every-mcp-server.md) | the usage probe starts every MCP server and is over the helper budget | — | nobody, the budget is set |
| [161](roadmap/161-drawing-a-frame-costs-41-ms-of-cpu.md) | drawing costs 41 ms a frame in 0.2.2 against a 10 ms, 10%-of-a-core budget | — | nobody, the budget is set |
| [162](roadmap/162-the-city-holds-gigabytes-of-gpu-memory.md) | the city holds 0.7–3 GB of GPU memory, system RAM on integrated graphics | — | nobody, the budget is set |
| [163](roadmap/163-a-hidden-city-keeps-all-of-its-memory.md) | a hidden city keeps all of its memory; ≤ 256 MiB within 30 s | — | nobody, the budget is set |
| [164](roadmap/164-no-soak-test-for-the-growth-budget.md) | an 8-hour soak test for the growth budget, on a release checklist | — | nobody, the budget is set |
| [165](roadmap/165-a-daemon-test-writes-into-the-real-state-directory.md) | a daemon test writes into the developer's real statistics store | — | nobody, a defect |
| [166](roadmap/166-lit-windows-are-round-halos-not-windows.md) | lit windows at night are round halos, not the building's windows; a mockup of every building first | — | nobody |
| [167](roadmap/167-the-cli-has-spread-and-ships-no-man-pages.md) | the command line has spread out (19 commands, ~40 global flags on each) and ships no man pages | — | Aria, the shape the analysis proposes |
| [168](roadmap/168-share-the-city-as-a-picture-gif-or-clip.md) | share the city as a picture, GIF or clip, in a sharing mode that hides names and spend | — | nobody |
| [169](roadmap/169-the-city-opens-with-every-session-arriving.md) | the city opens with every live session sailing in and being built, so they are bare lots for seven seconds | — | nobody, a defect; next patch |
| [170](roadmap/170-the-minimap-spills-out-of-its-panel-after-a-turn.md) | after a turn the minimap comes up at fit and its map spills out of its panel onto the footer | — | nobody, a defect |
| [171](roadmap/171-the-strip-says-1-need-you-and-1-prs.md) | the strip reads "1 need you", "1 prs", "1 errors", "1 subagents" | — | nobody, a defect |
| [172](roadmap/172-the-key-reference-misses-u-and-rebound-keys.md) | the key reference leaves out `u` and shows five rebindable keys at their defaults | — | nobody, a defect |
| [173](roadmap/173-new-session-names-a-session-by-its-id.md) | New session explains its group guess with a session id instead of a title | — | nobody, a defect |
| [175](roadmap/175-the-terminal-table-cuts-text-by-bytes.md) | the terminal table cuts titles and lines by bytes, breaking non-ASCII text | — | nobody, a defect |
| [176](roadmap/176-the-terminal-table-does-not-scroll.md) | the terminal table does not scroll; past the window it loses its header and the cursor | — | nobody, a defect |
| [177](roadmap/177-the-layers-stills-show-the-wrong-lenses.md) | the demo's "Spend" and "Context pressure" stills show Work and Cost, and the website publishes them so | — | nobody, a defect |
| [178](roadmap/178-the-design-docs-still-describe-nine-views.md) | `DESIGN.md` and `design/info-views.md` still describe nine views and two projections | — | nobody, a defect |
| [179](roadmap/179-group-lines-are-drawn-over-buildings.md) | group lines are drawn over the buildings they pass behind | — | nobody |
| [180](roadmap/180-the-lens-panels-wording-disagrees-with-the-strip.md) | Attention, Work and Cost panels say things that read as wrong beside the strip | — | nobody |
| [181](roadmap/181-small-polish-mcp-calls-f-and-0-model-ids-finder-rows.md) | small polish: "6 mcp" is calls, `f` and `0` listed twice, full model ids in `status`, finder rows cut with no ellipsis | — | nobody |
| [182](roadmap/182-the-reading-pane-shows-markdown-raw.md) | the reading pane shows Claude's Markdown as raw text | — | nobody |
| [183](roadmap/183-the-top-down-draw-path-is-unreachable.md) | `pkg/render` still carries the top-down drawing path, which the app no longer reaches | — | nobody, dead code |
| [184](roadmap/184-the-bar-names-a-session-triage-skips.md) | `bar` names and counts sessions triage has marked done or snoozed, so it disagrees with the footer | — | nobody, a defect |
| [185](roadmap/185-the-landmarks-stay-dark-at-night.md) | the landmarks (library, City Hall, power plant) stay dark at night | 166 | nobody |
| [186](roadmap/186-item-sessions-land-side-by-side-and-time-out.md) | item sessions run full suites side by side and time out: `make land` with a lock, serial lint, and the kickoff | — | nobody, a defect |
| [phase 20 item 3](roadmap/phase-20-explain-itself.md) | the plant's *reading* — the geometry was fixed at r186 and has not been looked at since | — | Aria, from a frame |

## Waiting on Aria

- **The plant's reading.** Wants a frame, not a measurement.
- **The validation checklist** has its own file, [`validation-checklist.md`](roadmap/validation-checklist.md). **Steps 1 and 8 pass** — step 1 now reconciles by session id rather than by title, which is what item 71 bought. **The other eight need her hands on the keyboard**, and the file says which keys.
- **The plant frames are rendered and waiting** — `docs/screenshots/r320-plant-fountain-aligned.png` and `r320-plant-fountain-behind.png`, the camera turned 180° between them so the fountain moves out from under the flange. If the flange reads as an underside in the first and not the second, the fountain's alignment is the cause; if it reads the same in both, the flange is. Read the premise note on items 23 and 33 first — the flange description was derived from a piece that is no longer the one drawn.
- **Item 149** — what 1.0.0 promises: strike or add entries on its list.
- **Item 69** — whether 10% is still the bar for a busy city, or was always the bar for an idle one.

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
