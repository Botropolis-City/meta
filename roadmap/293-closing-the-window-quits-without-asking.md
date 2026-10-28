# 293. Closing the window quits the city without asking, and nothing offers the tray

**Done 2026-10-28 (`210898f`, r1201). Filed 2026-10-26 (r1124), from Aria's use of 0.3.2. Nobody's call — Aria ruled the default and the trays.**

Depends on: 292
Landed: slice 1 (`b8d2063`, r1168).
Landed: slice 2 (`2aea1ad`, r1198).
Landed: slice 3 (`8ea5fa0`, r1200).

Aria, 2026-10-26: *"we should be catching closing the window and popping up the quit menu. I use mod+shift+q on my i3, but I assume it's the same as clicking the x if I had a DE ... we should allow minimizing to tray on quit as a setting rather than showing the quit menu ... Right click exit on the taskbar item would give us the quit/close up popup. Clicking the x would follow the setting of either showing the popup if it's a real exit or just minimizing to taskbar"*.
Asked, she ruled the default is to **ask**, and the tray must work on both Linux standards.

i3's kill sends the window manager's close request (`WM_DELETE_WINDOW`), the same a desktop's X button sends; nothing in `pkg` handles it today (no `ebiten.SetWindowClosingHandled`), so the window closes and the city exits at once.

## The fix

1. **Catch the close request** with `ebiten.SetWindowClosingHandled(true)` and `ebiten.IsWindowBeingClosed()`, and act on a new setting `on_close`: `ask` (the default) shows item 292's quit prompt; `tray` hides the window and keeps the city running in the tray.
2. **A tray icon** while the city runs, on Linux through StatusNotifierItem, falling back to the XEmbed system tray when no StatusNotifierItem host is on the session bus, so it shows on Waybar, KDE and GNOME's extension, and on i3bar and polybar; on macOS in the menu bar.
   Its menu: **Open the city** (also a left click), and **Quit…**, which shows the window and the quit prompt with *close up*.
   When no tray can be found, `on_close = tray` falls back to asking, and the settings panel says why.
3. The setting is a row in the settings panel and documented in `botropolis-config(5)`.
4. A hidden city costs what an unwatched one does (items 197, 214): it holds snapshots and draws nothing.
5. Tests: a close request with `ask` opens the prompt and does not exit; with `tray` it hides the window and does not exit; *Open the city* shows it; *Quit…* shows the prompt; no tray host falls back to asking; the XEmbed fallback is chosen only when no StatusNotifierItem watcher answers.
6. Frames for Aria: the tray icon and its menu on her i3, and the prompt after a close request.

## Closed

Slice 1 shipped in 0.3.3, on Aria's ruling that the release take it alone: the close request is caught and held until the key path answers it, `on_close = ask` opens item 292's quit panel, and `tray` hides the window where a tray exists and asks otherwise, with the settings row saying why.
`pkg/render/closewindow_test.go` holds each case, and `on_close` is in the settings panel, `botropolis-config(5)` and the surface test.

Slices 2 and 3 are `pkg/tray`, written by hand rather than taken from a library, because every build runs without cgo, which rules out every tray library that links GTK or Cocoa.
The one new dependency is `github.com/godbus/dbus/v5` (BSD-2-Clause, pure Go); XEmbed uses xgb, already a dependency.
StatusNotifierItem is chosen whenever a watcher with a host answers, and XEmbed only where a manager owns the selection and no such host does.
The icon is the logo's twelve polygons drawn in code.
The menu is *Open the city* and *Quit…*, with *Quit…* kept last so entries can go above it.
On XEmbed, which has no menu protocol, the menu is the city's own small window, set in Inter.
`testing/integration/tray/` runs both against a private `dbus-daemon` and Xvfb with XTEST clicks, and CI installs `dbus`, so both fail rather than skip there.

The frames are `botropolis/docs/screenshots/r1200-item-293-tray-icon.png` and `r1200-item-293-tray-menu.png`, on i3bar under Xvfb.
Filming them caught two defects, both fixed test-first: the fixed face drew *Quit…*'s ellipsis as a box, and the menu opened over the bar.

Deviations, for Aria:

- **macOS's menu bar is item 296**, because nobody here can run a Mac; until it lands, `on_close = tray` asks there.
- **There is no frame of the prompt after a close request.** The manager waived it, since it is the same panel Aria approved in item 292.
- **Hiding to the tray and coming back was not driven end to end** in the real city. It is `ebiten.SetWindowVisible`, and a hidden window takes the unwatched path of items 197 and 214, but it is on Aria's list to try once on i3.
- On i3bar, which offers no 32-bit visual, the icon keeps its square dark plate.
