# 201. The daemon sends the whole snapshot on every update, so a watching city can't idle

**Open. Filed 2026-10-22 (r889), from item 197's measurements. Nobody's call — Aria's dashboard ruling sets the budget.**

Depends on: 197

Aria, 2026-10-21, in item 197: *"I do want this to be able to just sit unfocused on another monitor so I can watch it as a dashboard"*, redrawn on changes only, aiming at 1% of a core. That overrides [item 22](022-cpu-and-memory-while-unwatched.md)'s rule that an unfocused city draws nothing.
[Item 197](197-the-city-lays-itself-out-again-on-every-snapshot.md) measured a city of 200 sessions in 150 projects, 25 of them live, with a line written every 200 ms and the daemon rescanning once a second: **about 220 KB of snapshot a second reaches the city, and decoding it (`encoding/json` in `proto.Client.readUpdate`) is 86% of a hidden city's CPU** — about 1.2% of a core before anything is laid out or drawn. Item 197's slice 4 unsubscribes a hidden city, but a watched one, focused or not, keeps paying it.

## The fix

The daemon sends what changed, not the whole snapshot: a full snapshot when a client attaches (or asks), then deltas (sessions added, removed, or changed field by field, and the rest of the snapshot's sections when they change), keyed so a missed delta forces a full resync. Item 159's scan-progress resends become a tiny delta. Check the protocol isn't part of item 149's promise (it isn't — the protocol is excluded), and keep `status --json` and `bar` (which are) unchanged.

Tests: a client fed deltas holds the same snapshot as one fed full snapshots, at every step of a replay; a missed delta resyncs; bytes per second on the item 197 fixture before and after; the unfocused-visible city's decoding and layout CPU (reported apart from drawing, which Xvfb does in software) ≤ 1% of a core, which turns item 197's unfocused case from "unmet" into a gate.

**Note from item 197** (2026-10-22): until this item lands, a hidden city drops its subscription and re-attaches for one snapshot every 5 s to keep the window title current, which keeps it under 1%. With deltas, staying subscribed while hidden may be cheap enough to drop that polling; measure it and decide here.
