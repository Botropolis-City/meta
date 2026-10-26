# 279. The map pans only with the left button, and Alt+drag never reaches the city on i3

**Fixed 2026-10-26 (`3ab7634`, r1127). Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria asked for both buttons.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: *"The drag to move is painful when there's districts everywhere ... holding alt and dragging isn't great either. What if we did right click drag as well? Also regardless, we should make mouse wheel click drag work."* And: *"also, the alt dragging isn't actually working"*.

Only the left button pans (`pkg/render/game.go`, the `g.dragging` path), and a left press on a district's floor or sign picks the district up, on the selected building carries it; Shift or Alt makes any drag pan (`panHeld`, `pkg/render/ghost.go`).
No other button is used anywhere in `pkg`.
Alt+drag fails on i3 because i3's default `floating_modifier` is Mod1, Alt, which i3 takes for moving windows, so the city never sees the press; it is not a Botropolis defect, but the help should not offer what a common desktop takes.

## The fix

1. A **right-button drag** and a **middle-button (wheel) drag** both pan, wherever the press lands, never picking up a district or a building.
2. Shift+drag stays; the help and man page name the right and middle drags first, and say Alt+drag may be taken by the window manager.
3. Tests, data-driven over the right and middle buttons and over a press on open ground, a district and the selected building: the drag pans and moves nothing.

## Answered while building

- **The design** (session's, approved by the manager, 2026-10-26): right and middle drags pan from anywhere through their own path, never picking up, carrying or selecting, and not under a scrim, as item 264; the footer reads *right drag: pan*; the help lists right and middle drags first and says Alt+drag may be taken by the window manager; the man page has no input section, so the in-app help, README and `design/city-and-rendering.md` carry it instead. They pan the City Plan too, through item 282's function.

## Closed

A right or middle drag now pans from wherever it starts and never picks up a district or carries a building (`pkg/render/buttonpan.go`).
It keeps its own state apart from the left drag, so its release clicks nothing, and it pans nothing under a scrim, matching item 264, except while sharing.
`TestButtonPan` covers both buttons over open ground, a district's floor and the selected building, and `TestSharingPointer` covers sharing.
The help lists the right or middle drag first and says Alt+drag may be taken by the window manager, and the footer offers "right drag: pan".

One deviation, agreed with the roadmap manager: the man page is unchanged, because botropolis(1) has no input section, so the README and `design/city-and-rendering.md` carry the change instead.
The right and middle drags call `Scene.Pan`, so they pan the City Plan once item 282 lands.
