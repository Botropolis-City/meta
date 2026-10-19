# 142. With the interface hidden, panels still open unseen and swallow keys

**Fixed 2026-10-19 (`c96d112`, r733). Filed 2026-10-19 (r724), from item 137. Nobody's call — a defect.**

Depends on: nothing

[Item 137](137-escape-skips-the-sidebar-and-the-hidden-interface.md) put the hidden interface at the top of Escape's ladder.
Working it, its session found that while the interface is hidden (`h`), `s`, `t` and `x` still open settings, the timeline and the breakdown, unseen, because `handleKeys` (`botropolis/pkg/render/keys.go`) routes keys to an open panel before it reaches the ladder.
The invisible panel then takes the keys that follow, Escape included, which closes the panel and leaves the interface hidden; the map seems not to answer.

## The fix

While the interface is hidden, a key that opens a panel shows the interface first and opens the panel (the panel's key says "show me this"), or does nothing; never an unseen panel. Choose the first, since it does what was asked.

Tests: hidden + `s` → it should show the interface and open settings; hidden + `t` and `x` likewise; no panel is ever open while the interface is hidden.

## Closed

`handleKeys` now ends by showing the interface whenever settings, the timeline or the breakdown is open, so no panel is ever open while it is hidden (`c96d112`, r733; changelog `321befd`).
That one check also covers a click on the power plant while hidden, which opened the breakdown unseen the same way and was not named above.
`pkg/render/hidden_test.go` presses `s`, `t` and `x` with the interface hidden and clicks the plant, and checks that every case leaves no panel open behind it.

One deviation, agreed with the roadmap manager: `h` with a panel open stays the panel's key, because every key goes to an open panel first and `h` is vim-left in settings.
The tests pin it: `h` with a panel open keeps the interface shown.
