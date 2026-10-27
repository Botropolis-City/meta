# 296. The city has no menu-bar item on macOS

**Open. Filed 2026-10-26 (r1153), split from item 293, which nobody here can test on a Mac. Nobody's call — Aria ruled the tray in item 293.**

Depends on: 293, 245

Item 293 gives the city a tray on Linux, with StatusNotifierItem first and XEmbed behind it, and an `on_close` setting whose `tray` value hides the window there.
On macOS the same belongs in the menu bar: an `NSStatusItem` with an `NSMenu` of *Open the city* and *Quit…*, written through `purego/objc` as `pkg/hotkey/darwin.go` is, behind item 293's `pkg/tray` seam, with `on_close = tray` hiding the window there too.

Until it lands, macOS reports no tray and `on_close = tray` falls back to asking, as item 293 provides.

## When it starts

Once item 293's seam is on main and a Mac is reachable through item 245's machines, so it is run on a Mac before it lands: the item opens, its menu's two entries deliver *Open* and *Quit*, a left click opens the city, and closing the window with `on_close = tray` hides it and leaves the menu-bar item.
