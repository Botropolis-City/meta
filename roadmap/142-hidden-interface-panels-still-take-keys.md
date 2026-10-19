# 142. With the interface hidden, panels still open unseen and swallow keys

**Open, in progress since 2026-10-19 in the session "item 142". Filed 2026-10-19 (r724), from item 137. Nobody's call — a defect.**

Depends on: nothing

[Item 137](137-escape-skips-the-sidebar-and-the-hidden-interface.md) put the hidden interface at the top of Escape's ladder.
Working it, its session found that while the interface is hidden (`h`), `s`, `t` and `x` still open settings, the timeline and the breakdown, unseen, because `handleKeys` (`botropolis/pkg/render/keys.go`) routes keys to an open panel before it reaches the ladder.
The invisible panel then takes the keys that follow, Escape included, which closes the panel and leaves the interface hidden; the map seems not to answer.

## The fix

While the interface is hidden, a key that opens a panel shows the interface first and opens the panel (the panel's key says "show me this"), or does nothing; never an unseen panel. Choose the first, since it does what was asked.

Tests: hidden + `s` → it should show the interface and open settings; hidden + `t` and `x` likewise; no panel is ever open while the interface is hidden.
