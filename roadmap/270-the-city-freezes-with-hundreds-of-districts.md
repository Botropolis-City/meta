# 270. The city freezes with hundreds of districts and groups of hundreds

**Fixed 2026-10-27 (`98a4654`, r1177). Filed 2026-10-26 (r1099), from Aria's start of 0.3.1 on another laptop with a long history. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`284256c`, r1102).
Landed: slice 2 (`f3fc805`, r1107).
Landed: slice 3 (`3d39de9`, r1108).
Landed: slice 4 (`98a4654`, r1177).
Landed: slice 5 (`6c3ea21`, r1109).
Landed: slice 6 (`5aaca19`, r1118).
Landed: slice 7 (`2729528`, r1125).
Landed: slice 8 (`25a1fe3`, r1134).
Landed: slice 9 (`bf4fe1e`, r1135).
Landed: slice 10 (`31591d3`, r1142).
Landed: slice 11 (`6d3578d`, r1162).
Landed: slice 12 (`0a0290a`, r1165).

Aria, 2026-10-26: *"We have way too many districts/groups/sessions. Every single tmp directory and probably work tree dir and such got its own district with one session and groups were generated for all of it. The UI is frozen and unusable, but at least the CPU and memory didn't spike to 100."*
Minutes later the city would not exit either.

What that laptop holds, measured read-only over ssh: 1,558 catalogued sessions in 559 distinct directories, so 559 districts; 48 groups, the largest with 781, 182, 91, 86, 72, 65 and 61 members.
The frozen city sat at about 2 GiB resident, sleeping, with 28 threads and under 10% of a core; the daemon was well.
The performance suite's largest city is 200 sessions in 150 projects, and `TestDaemonWithTwoThousandSessions` puts its sessions in a few directories, so nothing has ever drawn hundreds of districts.

Items 271 to 274 take most of those districts and groups off that map; this item makes the city survive them anyway, since a large real history is a fact of some machines.

## Where it costs (from a read of the code at r1099; to be confirmed by a profile)

- Per frame, unculled: each district's monument, sign and plate check (`pkg/render/iso.go`, around 782–868) and the top-down loops (`pkg/render/game.go`, around 1028).
- Group lines are drawn twice a frame, unculled, every stroke and station with a hit box (`pkg/render/iso.go` around 880; `pkg/render/lines.go` `groupLines`).
- Label layout is O(n²) per frame (`pkg/render/labellayout.go` `layoutLabels`), fed a plate per district plus station labels.
- Per snapshot: `placeLines` (groups × buildings) with `coordinator` rebuilding a district map per group (`pkg/city/lines.go`), and `plan.assign` rebuilding ring slots per new district (`pkg/plan/plan.go`), about O(n²).
- A freeze at low CPU also fits the main loop blocked rather than busy, so the first step is a goroutine dump of a frozen city (`SIGQUIT`) and a CPU profile, not a guess.

## The fix

1. A staged city at that laptop's scale — 600 districts, 1,600 sessions, groups of 800 — built from `botropolis-demo synth-home` (item 248), never from a real history, as a performance-tier case; first make it reproduce the freeze.
2. Profile it, fix what dominates, cull what is off screen (signs, monuments, plates, lines) and make the label layout sub-quadratic.
3. Gate it: the city at that scale opens, pans and quits, within the performance budgets, and the case stays in the suite.
4. Quitting must always work: `q` then `y` exits even when a frame or a snapshot is slow.

## Answered while building

- **Slice 4's measurement at the stress scale** (session, 2026-10-26; synthetic, 2,400 sessions in 900 districts, a group of 800, real city under Xvfb on its own daemon, a busy machine): first frame 13.5 s against a map within 5 s; Private_Dirty peak 936 MiB, within 1 GiB; settled 693 MiB against 512; drawing 34–55 ms a frame (40 quiet) against 10 ms of CPU. Without a daemon, 1.3 GiB peak and 940 MiB settled, because group detection runs in the city. About 36% of the fitted frame is item 212's noting and dry pass and 20% the depth sort.
- **Whether the case lands red** (manager, 2026-10-26): neither red nor loosened; slice 4 stays unlanded until Aria sets the bars at this scale, since a red performance-tier case would fail 0.3.2's pre-release run over a scale the release does not claim, and reporting instead of gating would loosen a limit without her. Meanwhile the session looks at the first frame (whether the first-launch progressive map fails at this size, which would be a defect) and at the ~490 MB outside the Go heap.
- **The bars at the stress scale** (Aria, 2026-10-26: *"we should set a limit far lower than that. What do you reasonably recommend?"*, then *"Looks good"* to the manager's recommendation): the city of 900 districts and 2,400 sessions is held to the budgets every city has, a map within 5 s, 1 GiB peak and 512 MiB settled, and to 10 ms of CPU a frame zoomed in or panning; only the fitted view, with every building on screen, gets 16 ms, one frame at 60 Hz. Slice 4 gates all five. A soft memory limit for the city is a separate question for her.
- **Memory at the stress scale** (Aria, 2026-10-26, asked by the manager with item 270's figures: settled 562 MiB after item 212's option 0, a 342 MB heap for 170 MB live): a soft memory limit plus trimming. The city sets a soft limit of about 400 MiB of Go heap at start unless `GOMEMLIMIT` is set in its environment, and live data keeps being cut so the limit rarely bites.
- **The soft limit's figure** (Aria, 2026-10-26, on the session's measurement): 300 MiB, not about 400. At 400 the limit never bites, since Go already settles under it; about 180 MB of the city lies outside Go, so Go must stay under about 300 MiB for the process to fit 512 MiB. At 300 the stress city settles at 470 MiB, with 1% of CPU on collection and frame times unchanged within noise.

## Closed

The freeze was not a hang: a goroutine dump of the staged city showed the game loop busy drawing, at about 8 frames a second, and the quit prompt standing down on the wall clock while a slow loop read the `y` late.
Twelve slices took the same staged history from 13.5 s to its first map, 693 MiB settled and 120 ms a fitted frame, to the five bars Aria set at this scale, which `TestACityOfSixHundredDistricts` and `TestACityOfSixHundredDistrictsFrames` (`testing/acceptance/bigcity_test.go`, performance tier) now hold it to.
On the performance manager's quiet run it opened its map in 3.8 s, peaked at 666 MiB, settled at 482 MiB, and drew every frame under its bar; each frame measure logs its margin.

- Per frame: a building's inspector without a pass over every building (1); off-screen drawables and labels culled, and the label layout on a grid (2); a district index, signs' moves worked out once a build, and a footprint test before a building's sprite bounds (7); the minimap's map painted once a city (8); the triage walk over only the sessions that need you (11); the depth sort by positions and then repaired from the last frame's order (6, 12).
- Opening: planting the ground against nearby blocks only, 3.4 s to 0.65 s of the first build on the game loop (5); group detection scoring only the pairs its wording could tie, 987,148 pairs to 37,595 and 2.8 s to 0.8 s of the daemon's first load (10).
- Memory: the city holds Go's memory to 300 MiB unless `GOMEMLIMIT` is set (9, Aria's figure).
- Quitting: the prompt stood down only once 10 s and 100 updates had both passed (3); item 292's quit panel has since replaced the prompt, and it waits for an answer.

Changelog: 0.3.2's *A city with hundreds of districts opens and stays usable* (slices 1, 2, 3, 5), and item 297's entry under *Changed* for slices 6–12 and the memory limit.

For Aria, where it differs from what the item asked:
the staged history is 2,400 sessions in 600 districts, its 300 temporary directories folded into one by item 272, with its group of 800 tied by a shared ticket rather than by timing, since item 271 ended timing chains;
the frame bars are measured as median thread CPU through the headless driver, because zoom and pan cannot be driven in a real city under Xvfb, while the first map and memory are measured on the real city and its daemon.
