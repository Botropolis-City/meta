# 293. Closing the window quits the city without asking, and nothing offers the tray

**Open, in progress since 2026-10-26 in the session "item 293". Filed 2026-10-26 (r1124), from Aria's use of 0.3.2. Nobody's call — Aria ruled the default and the trays.**

Depends on: 292

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
