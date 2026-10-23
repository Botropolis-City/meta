# 201. The daemon sends the whole snapshot on every update, so a watching city can't idle

**Fixed 2026-10-22 (`df3fbbe`, r913). Filed 2026-10-22 (r889), from item 197's measurements. Nobody's call — Aria's dashboard ruling sets the budget.**

Depends on: 197
Landed: slice 1 (`120b5b3`, r907).
Landed: slice 2 (`a085aed`, r910).
Landed: slice 3 (`df3fbbe`, r913).

Aria, 2026-10-21, in item 197: *"I do want this to be able to just sit unfocused on another monitor so I can watch it as a dashboard"*, redrawn on changes only, aiming at 1% of a core. That overrides [item 22](022-cpu-and-memory-while-unwatched.md)'s rule that an unfocused city draws nothing.
[Item 197](197-the-city-lays-itself-out-again-on-every-snapshot.md) measured a city of 200 sessions in 150 projects, 25 of them live, with a line written every 200 ms and the daemon rescanning once a second: **about 220 KB of snapshot a second reaches the city, and decoding it (`encoding/json` in `proto.Client.readUpdate`) is 86% of a hidden city's CPU** — about 1.2% of a core before anything is laid out or drawn. Item 197's slice 4 unsubscribes a hidden city, but a watched one, focused or not, keeps paying it.

## The fix

The daemon sends what changed, not the whole snapshot: a full snapshot when a client attaches (or asks), then deltas (sessions added, removed, or changed field by field, and the rest of the snapshot's sections when they change), keyed so a missed delta forces a full resync. Item 159's scan-progress resends become a tiny delta. Check the protocol isn't part of item 149's promise (it isn't — the protocol is excluded), and keep `status --json` and `bar` (which are) unchanged.

Tests: a client fed deltas holds the same snapshot as one fed full snapshots, at every step of a replay; a missed delta resyncs; bytes per second on the item 197 fixture before and after; the unfocused-visible city's decoding and layout CPU (reported apart from drawing, which Xvfb does in software) ≤ 1% of a core, which turns item 197's unfocused case from "unmet" into a gate.

**Note from item 197** (2026-10-22): until this item lands, a hidden city drops its subscription and re-attaches for one snapshot every 5 s to keep the window title current, which keeps it under 1%. With deltas, staying subscribed while hidden may be cheap enough to drop that polling; measure it and decide here.

**Note from item 202** (2026-10-22): item 197's `TestAnUnwatchedCityUnderAStreamOfSnapshots` runs two serial cases of about a minute each (20 s settle, 30 s stream, start-up), and pushed CI's acceptance suite past its 10-minute timeout. Item 202 raised the CI timeout; when this item reworks that test, make it cheaper (shorter windows, or the two cases in parallel if that does not skew their CPU shares).

## Slices

Planned with the roadmap manager on 2026-10-22, which approved the test trees and ruled on the questions below.

1. **Deltas on the wire** (r907).
   A subscription is sent the whole snapshot once, then each update as what changed since what **that connection** was last sent.
   The daemon folds updates a slow subscriber has not taken into the newer one,
   so diffing against the last update sent, rather than against the daemon's previous view, is what makes a fold leave no gap.
   Sessions and groups are diffed by ID, field by field at the top level, and every other section is resent whole when it changes.
   Groups are diffed too because a group's journal moves with every line a member writes: resending every group was 14 KB an update on item 197's city (the manager, 2026-10-22: go a level deeper only where one field dominates the bytes).
   A delta that would not be smaller, or a list whose IDs repeat, goes as the whole snapshot.
   The client applies deltas inside `proto`, so the feed and the city still get whole snapshots, and a delta on a base it does not hold ends the stream, after which the feed attaches again for a whole one.
   The protocol went from 1 to 2 (the manager: outside item 149's promise), and a protocol-1 daemon is refused with item 152's dialog, not a hang.
   On item 197's city, with a line every 200 ms: **262.6 KiB/s of whole snapshots became 0.5 KiB/s** on the wire (`TestTheStreamOnABusyCity`, gated at 5%).
   Under Xvfb the unfocused city still measured 16.6% of a core outside the software rasteriser and 45.5% in it: drawing on its own thread plus laying out, which slice 2 separates.
2. **The unfocused gate**: the city counts its own time decoding and laying out snapshots, and that is gated at 1% of a core, with process CPU logged beside it on every run.
   **Aria's 1% for the dashboard is the whole process, drawing included.**
   Xvfb draws in software, so drawing cannot be measured meaningfully there: the gate covers decoding and layout, and the whole process is measured on real hardware by the benchmark session once this slice lands (the manager, 2026-10-22).
   Landed r910. The client times only the decoding of each line, not the wait for it, and the frame timer's QUIET line carries `snapshots=`, `decoding=` and `layout=`.
   Decoding was then 0.09% of a core; laying out was 0.85%, because `city.build` still runs whole for a snapshot that moves only activity times (about 7 ms on the real-sized city), which left the gate at 0.93%.
   A fifth of `build` was naming the districts by holding every root against every other, so the tails are now counted once each, against the old naming kept as an oracle (`TestDistrictNamesAgreeWithTheOracle`, 4× on 200 roots): **0.72% of a core**, 11 ms decoding and 97 ms laying out in 15 s, at a load average of 12. Process CPU, logged beside it: 8.6% outside the software rasteriser, 29% in it.
   The rest of `build` (placing groups, lines and streets, and the garbage it makes) is not incremental yet: that is [item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md).
   The test now settles on the frame timer's first line instead of 20 s and streams 15 s instead of 30. Its two cases stay serial, because the X helpers set `XAUTHORITY` for the process, which `t.Parallel` forbids.
3. **A hidden city's subscription**: measure staying subscribed while hidden against the 5 s glance, and drop the glance if it costs no more.
   Landed r913. Two runs each on item 197's city over 15 s: the glance cost 0.66% of a core and read 659–707 KiB; staying subscribed cost 0.53–0.60% and read 7 KiB.
   So the glance is gone (the manager, 2026-10-22), and a hidden city stays subscribed, holding its snapshots and laying out none until it can be seen.
   **This reverses item 197's deviation that a hidden city's title is up to 5 s behind**: it says at once again that someone needs you.
   The hidden case now asserts it was streamed what changed and read no whole snapshot.

**Measured on the real GPU, quiet desk** (benchmark session, 2026-10-22, 265U iGPU, real history, unfocused and visible, 450 s): r910 used **0.90% of a core** mean (p95 2.9%, max 15.6%), r905 0.80% — only one or two transcripts were written during the runs, so this is the quiet case and the two builds cannot be told apart; a controlled busy run (replayed writes) is being taken. Of r910's 0.90%, the Go side is about 0.33%; the rest is GL driver and C time. Raw: `~/.local/state/botropolis-perf/unfocused-r910-real-20261022-171721/`.

## Closed

Fixed in three slices, r907–r913.
The daemon sends a subscription the whole snapshot once and then what changed, and on item 197's city of 200 sessions that took the stream from 262.6 KiB/s to 0.5 KiB/s (`TestTheStreamOnABusyCity`).
A client fed deltas holds the same snapshot as one fed whole snapshots at every step of a replay (`TestDeltas`), and a delta on a base it does not hold ends the stream, so the city attaches again for a whole one.
`TestAnUnwatchedCityUnderAStreamOfSnapshots` now gates both cases at 1% of a core: a hidden city on its process CPU (0.53%), and an unfocused, visible one on the time it counts decoding and laying out (0.72–0.79%), with its process CPU logged beside it.
The test costs about 35 s a case instead of a minute.

**Deviations, for Aria:**

- **The unfocused gate covers decoding and laying out, not the whole process.** Your 1% for the dashboard is the whole process, drawing included, and a virtual display draws in software, so drawing is measured on the real GPU instead: 0.90% of a core on a quiet desk (the note above), with a busy run still to come.
- **Laying out is most of what is left**, about 7 ms a snapshot, because the city still lays itself out whole for a snapshot that moves only activity times; that is [item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md).
- **Two changes outside the protocol**: the districts are named in linear time, against the old naming kept as an oracle, which bought the gate its margin; and the hidden city's 5 s glance is gone, so its title is current again.
- **The test's two cases stay serial**, not parallel as item 202 suggested, because the X helpers set `XAUTHORITY` for the whole process.
