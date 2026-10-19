# 137. Escape skips the sidebar and the hidden interface, and opens settings over them

**Open, in progress since 2026-10-19 in the session "item 137". Filed 2026-10-19 (r707), from the validation checklist's step 6 run against main before 0.2.0. Nobody's call — a defect.**

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
