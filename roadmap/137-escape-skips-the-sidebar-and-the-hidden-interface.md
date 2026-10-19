# 137. Escape skips the sidebar and the hidden interface, and opens settings over them

**Fixed 2026-10-19 (`d99b81f`, r712). Filed 2026-10-19 (r707), from the validation checklist's step 6 run against main before 0.2.0. Nobody's call — a defect.**

Depends on: nothing

Step 6 of the [validation checklist](validation-checklist.md): `b`, `t`, `s`, `?`, `h`, `r`, `n`, `/` each open, close with Escape, and none leaves the map wrong.
Screenshotted after each key and after the key plus Escape on 2026-10-19: the timeline, settings, the reference and the finder close; `r` and `n` are one-shot and Escape then opens settings, as bug 43 intended.
Two are not on Escape's ladder (`botropolis/pkg/render/keys.go`, the rungs before "the last rung back is settings"):

- **The sidebar** (`b`): Escape leaves it open and opens settings on top of it.
- **The hidden interface** (`h`): Escape opens settings *while the interface is hidden*, so an invisible panel takes the keys that follow.

Bug 43a's own comment is the rule this breaks: "the list of things Escape closes has to be the list of things that are open, whatever opened them."

## The fix

Put both on the ladder, above settings: Escape closes the sidebar, and Escape with the interface hidden shows it again. Settings stays the last rung.

Tests, in the existing ladder's table: sidebar open + Escape → it should close the sidebar and not open settings; hidden + Escape → it should show the interface and not open settings.

## Closed

Both are on the ladder now (`botropolis/pkg/render/keys.go`, `d99b81f`, r712), and the changelog says so under *Fixed* (`16421d7`, r724).
Escape with the interface hidden shows it again and does nothing else, at the top of the ladder, because `h` hides the card, the sidebar and the view key along with everything else, so any other rung would be a change nobody could see.
The sidebar is the rung just above settings, below the map's own states (selection, focus, view key, City Plan, lens), and settings stays the last rung.

Deviation, for Aria: the item asked for the tests "in the existing ladder's table", but no table of the ladder existed; its rungs were tested one at a time in other files.
The new one is `botropolis/pkg/render/escape_test.go`, `TestEscapeLadder`: sidebar open, hidden, hidden with the sidebar open (one rung per press, so the sidebar stays), and nothing open, which still opens settings.
The roadmap manager approved the tree and the placement.

Found while working it, not fixed here, to be filed: while the interface is hidden, the settings, timeline and breakdown panels still take keys.
`s`, `t` and `x` open them unseen, since `handleKeys` routes to an open panel before it reaches the ladder, and the same invisible panel then swallows the keys that follow — Escape included, which closes the panel and leaves the interface hidden.
