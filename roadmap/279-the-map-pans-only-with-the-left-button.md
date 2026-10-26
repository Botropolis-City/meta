# 279. The map pans only with the left button, and Alt+drag never reaches the city on i3

**Open, in progress since 2026-10-26 in the session "item 279". Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria asked for both buttons.**

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
