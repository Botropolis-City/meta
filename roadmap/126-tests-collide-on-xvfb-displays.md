# 126. Tests started at the same time collide on one virtual display

**Open, in progress since 2026-10-18 in the session "item 126". Filed 2026-10-18 (r636), from what item 114 measured. Nobody's call — a defect.**

Acceptance tests run the city under `xvfb-run -a`, which picks a free display number by looking for one; several starting at once can pick the same one, and the second Xvfb, or the city on it, loses its X server.
Xlib then calls C `exit(1)` ("X connection broken" / XIO fatal), so no Go cleanup runs; in item 114's runs, 5 of 8 that left a private directory behind had shared display `:484`, and `xvfb-run`'s own `kill` found Xvfb already gone.
It only shows when several sessions or packages run acceptance tests at once, which is now the normal case on this machine.

## The fix

Give each test its own display without a race: start Xvfb with `-displayfd` so the server itself reports the number it took, or have each test pick a display it owns (`xvfb-run -n` with a number from a lock), in the helper every test uses.

Tests: many headless runs started at once should each get a display of their own and none lose its X server; a guard that no test calls `xvfb-run -a` directly.

## Answered while building

- **The fix** (manager, 2026-10-18): a `pkg/xvfb` starts the server with `-displayfd`, so the server itself reports the display it took, and a random authorisation cookie written in Go, so no other local user can connect; every headless city and every test that needs a display goes through it, and a guard refuses `xvfb-run` anywhere in the code, the Makefile, `tools/` or the workflows. The `xvfb-run` dependency goes from every package for the one that ships Xvfb itself; `tools/measure-render`'s deliberately named display stays.
