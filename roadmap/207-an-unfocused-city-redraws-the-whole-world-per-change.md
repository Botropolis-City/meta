# 207. An unfocused city redraws the whole world on every change, without the standing city

**Open, in progress since 2026-10-22 in the session "item 207". Filed 2026-10-22 (r916), from the benchmark session's busy run after item 201. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: 206 (slice 2)
Landed: slice 1 (`47bb513`, r930).
Landed: slice 2 (`bf9ef91`, r942).
Landed: slice 3 (`8b33db9`, r946).

Measured on the 265U's GPU (real history linked read-only into a scratch home, two sessions each writing a line every 200 ms, 450 s; raw in `~/.local/state/botropolis-perf/busy-unfocused-{r910,r905}-real-20261022-184541/`): **an unfocused, visible city at r910 averaged 2.74% of a core (p95 4.9%) against 1%** — r905 3.60%. It drew a frame per change, about 360–480 frames, at 12–17 ms each, **with the standing-city layer never reused**.
Where it goes (300 s profile): Draw 57% — `drawIso` 45%, a full world redraw per change; overlays 12%, text 10% — then `SetSnapshot` → `city.build` 22% ([item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md)), GL flush 7%, GC 6%.
[Item 193](193-a-still-city-is-redrawn-whole-every-frame.md) composes the standing city once and redraws only what moves; [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md)'s gate covers decoding and layout only, since Xvfb draws in software, so this draw path went unmeasured until now.

## The fix

Find why the unfocused draw-on-change path doesn't use the standing city (its key changing on every snapshot, or the path bypassing it), and make a change that moves one building redraw only that building's rectangle, as a focused frame does. Then item 206's layout work takes most of the rest.

Tests: an unfocused city fed a change to one session's state recomposes the standing layer on no frame and draws only dirty rectangles (count it in the frame log, as item 193's tests do); re-measure busy on the GPU with the benchmark session's replay, against 1%.

## How it is being built (2026-10-22)

**The filed premise was wrong: the standing layer is reused.**
On the busy test city, unfocused on Xvfb with a session writing every 200 ms, the debug build's frame log reads `composes=0 redos=0 direct=0 rects=1` on every frame, so the GPU path does what item 193 built.
What a dashboard frame redraws whole is the dry pass, in CPU: every drawable runs and is recorded every frame, and the ground is recorded again on every snapshot, because its key carries `Scene.Generation()`.
The r910 profile puts Draw at 4.43 s of 7.71, about 14–18 ms of CPU a dashboard frame, against about 2 ms for a driven settled frame (item 193).
`agedLots` alone is 1.11 s, 14% of the whole process: each overgrown district's floor dressed again every frame (0.40 s), and one recorded mesh per crack segment (0.48 s).
The ground's re-recording is 0.49 s.
The first-run panel's text is 0.59 s, which item 161's slice 1 (r912) already bakes.
Headless, a dashboard frame of the metropolis (a snapshot fed, then a tick) is about 12 ms of draw CPU: group lines 2.2 ms (`dashed` records one mesh per dash), the ground's re-recording 2.2, the sorted dry pass 2.9 and chrome 1.5.

The plan, approved by the roadmap manager:

1. **A line is one mesh per drawable, not one per segment**: the aged lots' cracks and the dashed group lines, with the same triangles in the same order, so the pixels are the same; a line drawn while a night cutter is set keeps its own cut.
   And an aged district's floor is kept while everything `dressDistrict` reads of it holds — root, rung, depot, rect and its buildings' rects — so nothing hand-kept can go stale.
2. **The ground is not recorded again on a snapshot that changes nothing it draws**: `staticCity` keys on item 206's `Scene.GroundGeneration()` (its slice 2), which 206 guards with a test that the ground drawn equals a from-scratch build's whenever it holds.
3. **Measured again** on the GPU through the benchmark session, against 1%, with 206's layout work in; anything left is reported with a profile before more is done.

Tests: `TestDressingMemo` and `TestOneMeshPerLine` in `pkg/render`; `TestTheGroundOnASnapshot` for slice 2; `TestAnUnfocusedCityUnderAStreamOfChanges` in the acceptance suite, which is the item's own test and passed before any of this, so it lands as the guard the item asked for, not as a red test made green; `BenchmarkADashboardFrame`, reported, never gated.

**Slice 1 landed at r930.**
On a city of 150 overgrown projects (`BenchmarkTheAgedLots`), recording the aged lots took 36,894 allocations and 11.0 MB before, and 16,905 and 3.4 MB after.
On the metropolis, which has almost no overgrown lots, it does not show, and the dashed group lines cost what they did: their cost is the tessellation, not a command per dash.
`TestAnUnfocusedCityUnderAStreamOfChanges` passed before the slice, and fails when the standing city is drawn straight.

**Found while building, and fixed in slice 2** (the roadmap manager, 2026-10-23): the ground's key misses inputs that `composeStatic` reads.
These are the hovered road (`iso.go`'s street tint and `roadLines`), the hovered beam (`beams`), the hovered building's effect on which roads the highlight lights, and which kit atlas is chosen as its pages finish uploading.
So the pointer leaving a road for bare ground, or moving to another road, leaves the old highlight in the cached ground: `TestTheGroundKey` reproduces it, and a pointer that stays passes.
`--check-frames` could not see it, because the ground drawn straight is cached under the same key, so both sides go stale together.
Slice 2's key is 206's `GroundGeneration()` plus these render-side inputs, without `hoverLine` and `labels`, which `composeStatic` never reads.
Its check is randomised as well as tabled: seeded small changes to snapshots, the pointer and the atlas, asserting that whenever the key held, the cached ground is the ground composed fresh.

**Slice 2 landed at r942, and the plan is renumbered**: slice 2 became the ground's key fix, so keying on item 206's `GroundGeneration()` (206 slice 2, r932) is slice 3, and the measurement after it the last step.
Slice 2's key holds the hovered road and beam, a fingerprint of what the highlight lights and fades, asked as `composeStatic` asks it, and the chosen kit atlas; `hoverLine` and `labels` left it.
`TestTheGroundKey` holds each move red before the fix or under mutation, with controls that pass, and a seeded random walk of the pointer, the view and the selection found a removed road or highlight on its own, three runs of three.

**Slice 3's design** (the roadmap manager, 2026-10-23): the ground records no hover targets today, in any view, with or without kits, but it replays whatever it records, and those are pointers into the city they came from.
So the key also carries `Generation()` whenever the last compose recorded one, which corrects itself where a comment would not.
Its tests: a snapshot that moves only activity times records the ground on no frame; one that changes what the ground draws — an MCP call count, a road's file count, a new project, a team, a turn — keeps it as composed fresh; a planted hover target composes it again; and the random walk takes small snapshot changes too.
The busy GPU re-measure is booked by the roadmap manager for once 206's slice 3 and this slice 3 are both on main.

**Slice 3 landed at r946.**
A snapshot that moves only activity times records the ground on no frame, and `staticCity` no longer appears in a dashboard frame's profile.
`BenchmarkADashboardFrame` went from 6,113 allocations and 1.48 MB a frame to 4,996 and 1.13 MB; its time is about 5.3 ms of draw CPU against 7.1 before slice 1, on a loaded machine.
Mutating pkg/city's ground found a weak guard: the tabled road case could not fail, because without kits the ground draws roads as plain lines with no traffic tint, and it ran in the servers view.
The tests now draw from the kits and check every view; with MCP calls or roads left out of the ground, the tabled cases fail every time, and the random walk about half its runs, so the walk is the net for a field nobody listed, not the guard for the ones listed.

**The walk was made to exercise every kind of change on every run** (`846287a`, r948; the roadmap manager, 2026-10-23: *"don't make it longer"*).
Each kind of snapshot change comes once in a shuffled order before the random steps, and each always changes something.
That alone was not enough, and why is the lesson: the walk put the pointer on a fresh target each step, and a target is a pointer into the city, so every rebuild moved the key and composed the ground again, hiding the stale field.
A snapshot step is now composed with the pointer on bare ground before and after, where only the snapshot can move the ground.
With MCP calls, roads or camps left out of pkg/city's ground the walk fails four runs of four, at the same 150 steps.
What is left is the busy re-measure on the GPU, against 1%.
