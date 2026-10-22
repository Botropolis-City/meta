# 197. The city lays itself out again on every daemon snapshot, even hidden

**Fixed 2026-10-22 (`137078f`, r893). Filed 2026-10-21 (r876), from the laptop benchmark at r871. Nobody's call — a defect against the city's CPU budgets.**

Depends on: nothing
Landed: slice 1 (`ccca0c7`, r878).
Landed: slice 2 (`e28335b`, r882).
Landed: slice 3 (`b7e71d3`, r892).
Landed: slice 4 (`137078f`, r893).

A 60 s profile of the city on the real history (265U iGPU, `458454f`, r871, [report](../performance/reports/2026-10-21-ultra7-265u-igpu-r871.md)) puts **76% of an unfocused or hidden city's CPU in `Scene.SetSnapshot` → `city.build`**, which lays the whole city out again for every snapshot the daemon sends, whether or not anything that shapes the city changed. Within it:

- `group.Order`: 38% — regular expressions run over every site's words, and one regular expression **compiled per site and version** in `tagged`;
- `plan.Make` → `plantGround`: 29%.

It is most of [item 163](163-a-hidden-city-keeps-all-of-its-memory.md)'s CPU (a hidden city at 7.9% of a core, spikes to 34%, against 1%) and part of [item 161](161-drawing-a-frame-costs-41-ms-of-cpu.md)'s (a focused city at 83% of a core against 10%).

## The fix

Make a snapshot cost what changed in it: compile the regular expressions once; keep the ordering and the plan between snapshots and redo them only when their inputs change (sessions joining or leaving, groups, the layout); and, while the city is hidden, take snapshots without laying out until it is shown again.
From-scratch layout stays available as the oracle, as item 158 did for grouping.

Tests: a snapshot that changes only a session's state (working → waiting) lays out nothing again, and the city it draws equals the one built from scratch; a benchmark of `SetSnapshot` on a city the size of the real history (about 200 sessions in 150 projects) before and after; and an acceptance measure of a hidden city's **process CPU** under a stream of snapshots, against the 1% budget.

## Slices

Measured first with `BenchmarkSetSnapshot` (a synthetic city of 200 sessions in 150 projects, eight groups whose sessions carry 40 order lines each, 265U): 1.42 s a snapshot, 79% of it in `group.Order` and 13% in `plan.Make`.
Inside `group.Order`, `released` ran again for every pair of sites, `bumps` ran two expressions over every line for every version, and `waitsFor` and `tagged` compiled an expression on every call.

1. **`group.Order` reads each site once** (r878): 4.6 s to 28 ms for a group of 25 sites, and 1.42 s to 136 ms a snapshot.
   The order before is kept in `pkg/group/order_oracle_test.go`, and 400 generated groups read the same through both.
2. **The scene remembers its plans and its groups' orders** (r882), and makes or reads them again only when their inputs change; a wait on a site being done follows the site's state on every snapshot.
   A snapshot that changes one session's state went from 136 ms to 8.3 ms, and one that shapes nothing new, such as item 159's progress-only snapshots, makes no plan and reads no order.
3. **A city nobody can see holds its snapshots**: hidden (unmapped, as i3's scratchpad leaves it) or minimised, it lays out the newest once it can be seen again, and the window title follows every snapshot.
   **An unfocused city that can be seen is a dashboard** (Aria, 2026-10-21: *"I do want this to be able to just sit unfocused on another monitor so I can watch it as a dashboard"*), which supersedes [item 22](022-cpu-and-memory-while-unwatched.md)'s rule that an unfocused city draws nothing.
   Asked how it should draw, she chose **changes only**: it lays out each snapshot and paints one frame for it, and nothing moves in between.
   The acceptance measure runs both, hidden and unfocused under a change every 200 ms, each gated at 1% of a core; if the unfocused one cannot make it, the redraw rate under a stream is the lever, and that choice goes to her.
   Landed r892, measured under Xvfb against a daemon of 200 sessions in 150 projects, 25 live: hidden went from 6.0% to 1.1–1.8%, and a profile puts 86% of what is left in decoding the daemon's whole snapshot each second.
   Unfocused is 19.8% outside Mesa's software rasteriser threads, which includes Mesa's work on the city's own thread, and 47.6% in them.
   Both are targets that skip, printing the gap, until they are met by 0.8% or better, so a lucky run cannot fail someone else's landing.
   Item 201 (the daemon sends deltas) is what brings the unfocused case under; a first fixture with no live session streamed nothing and passed at 0.6%, so the test now checks the snapshots reached the city.
4. **A hidden city lets its subscription go**, and attaches for one snapshot every 5 s, so its title says within 5 s that someone needs you, and at once when it is shown again; events are taken from the newest the feed has seen, so none is lost or handed on twice (the roadmap manager, 2026-10-22).
   The hidden case becomes a plain gate at 1%.

## Closed

Fixed in four slices, r878–r893.
A snapshot of a real-sized city went from 1.42 s to 8.3 ms when one session's state changes (`BenchmarkSetSnapshot`), and the scene's city is tested against one built from scratch.
`TestAnUnwatchedCityUnderAStreamOfSnapshots` gates a hidden city at 1% of a core: 0.63–0.70% on the 265U under Xvfb, from 6.0%, against a daemon of 200 sessions in 150 projects, 25 of them live, with a change every 200 ms.

**Deviations, for Aria:**

- **An unfocused city now draws, as a dashboard** (her ruling in the item 197 session, 2026-10-21): it paints one frame per change, and nothing moves in between.
  It does not meet 1% yet: under Xvfb it measured 6.8–19.8% outside Mesa's software rasteriser, which includes Mesa's work on the city's own thread, so the figure overstates a real GPU's.
  On her desktop it is untested.
  That case stays a skipping target in the test and is carried by [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md), and the redraw rate is the lever if 201 is not enough.
- **A hidden city's title is up to 5 s behind**, because it looks at the daemon every 5 s instead of taking every update.
- **The test's skip margin**: an unmet target fails as met only below 0.8%, so run-to-run noise cannot fail someone else's landing.
