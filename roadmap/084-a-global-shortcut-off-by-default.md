# 84. A global shortcut that opens the finder from any application, off until the user sets one

**Open, in progress since 2026-10-16 in the session "item 84". Filed 2026-10-15 (r412) at Aria's request, from the planning session. Nobody's call for the X11 part; the macOS and Wayland parts each start with a spike.**

Depends on: 82 (slice 5)
Landed: slice 1 (`938625d`, r476).

What is being built: a setting that is off by default and that, once the user records a key combination, makes that combination open the finder ([item 82](082-find-a-session-by-what-was-said-in-it.md)) from any application and bring the city's window forward.
It is off by default so that no key — `Ctrl+K` least of all — stops meaning what it means in other applications.
`Ctrl+K` inside the city never becomes global.

## Rules it must keep

Item 82's, and two of its own:

- **The user's combination, or none.**
  There is no default shortcut.
  Botropolis grabs nothing until a combination is set, and releases it the moment the setting is cleared.
- **Say what does not work.**
  A combination another application already holds, or a desktop with no way to register one, is reported in the settings panel in words, with the fallback: bind `botropolis find` in the desktop's own keyboard settings.

## What exists to build on

- **The setting.**
  The settings panel (`pkg/ui/settings.go`, `SettingRow`) saves through `config.Save` (`pkg/app/module.go`), and a new key sits beside `config.KeyTerminal` in `pkg/config/config.go`, empty for off.
- **The window.**
  Ebitengine v2.10.2 runs on Linux as an X11 client only — its `internal/glfw` has no Wayland backend — so on a Wayland desktop the city is an XWayland window.
  It exposes no native window handle and no call that raises a window.
- **No cgo.**
  Each part below has to build with `CGO_ENABLED=0`.
- **The path it calls.**
  `botropolis find` and the single-instance city are item 82's fifth slice, and the shortcut calls the same path.

## The parts

| desktop | registering the combination | coming forward | confidence |
| --- | --- | --- | --- |
| X11 sessions: i3 and every other X11 window manager | a grab on the root window through a pure-Go X11 client such as `jezek/xgb`, made for every combination of the lock keys' masks, as X11 grabs require | `_NET_ACTIVE_WINDOW` with the key event's timestamp, the window found by its instance name or process id | known; i3 by default raises only on a visible workspace and marks the workspace urgent otherwise (`focus_on_window_activation`) |
| macOS | Carbon's `RegisterEventHotKey`, through `purego`, which Ebitengine already brings in | activating the application when the key fires | spike first: whether activation from a hotkey is honoured on current macOS |
| Wayland sessions | the desktop portal's `GlobalShortcuts` interface over D-Bus, with the pure-Go `godbus/dbus`, where the desktop implements it; the desktop may ask the user to confirm | the least certain part: raising an XWayland window after a portal activation | spike first: which desktops implement the portal, and whether the window can be raised |

The X11 part ships first.
Where a part is missing, the setting says so rather than half working.

## The setting

1. The settings panel gains *Global shortcut — off*.
2. Choosing it asks for a combination and records the next one pressed, and `Esc` cancels.
3. A combination already held elsewhere, or one that commonly means something in other applications (`Ctrl+K`, `Ctrl+P`, `Ctrl+Shift+P`), is named as such before it is saved, and can still be saved.
4. Clearing the setting releases the grab at once.

## Slices

1. **The X11 part.**
   `global_shortcut` in the config, `pkg/hotkey`'s grab and raise over `jezek/xgb`, and a press opening the finder by `botropolis find`'s path.
   It also raises the window for `botropolis find` on X11.
   Its commit calls it slice 1a.
2. **The settings row**, with its frames.
3. **The macOS spike**, written up here.
4. **The Wayland spike**, written up here.

## Done when

The X11 part works under i3, and under Xvfb with a bare X server that has no window manager, run in CI as well as here; the setting round-trips through the config file, the macOS and Wayland spikes are written up here with their verdicts, and Aria has judged the frames of the settings row.

## Answered while building

- **A second window manager:** none is installed for this; the raise is tested under Xvfb with i3 and with a bare server, and recorded as all it got. Aria, 2026-10-16, declining to install openbox.
- **Who holds the grab:** the city, so the shortcut works only while the city runs; a daemon holding it would make the daemon an X client, which nothing asked for. Manager, 2026-10-16.
- **Clearing the setting:** `Backspace` or `Delete` on the row clears it to off. Manager, 2026-10-16.

## Sources

- [`GlobalShortcuts` — XDG Desktop Portal documentation](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html)
- [`focus_on_window_activation` — i3 user's guide](https://i3wm.org/docs/userguide.html#focus_on_window_activation)
- [`jezek/xgb`, a pure-Go X11 client](https://github.com/jezek/xgb)
- [`godbus/dbus`, a pure-Go D-Bus client](https://github.com/godbus/dbus)
- [`purego`](https://github.com/ebitengine/purego)
- [`NSApplication.activate()` — Apple developer documentation](https://developer.apple.com/documentation/appkit/nsapplication/activate%28%29)
