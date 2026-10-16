# 84. A global shortcut that opens the finder from any application, off until the user sets one

**Open, in progress since 2026-10-16 in the session "item 84". Filed 2026-10-15 (r412) at Aria's request, from the planning session. Nobody's call for the X11 part; the macOS and Wayland parts each start with a spike.**

Depends on: 82 (slice 5)
Landed: slice 1 (`938625d`, r476).
Landed: slice 2 (`4f421a0`, r481).

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
2. **The settings row**, with its frames: `botropolis/docs/screenshots/r481-item-84-shortcut-off.png`, `-asking.png` and `-named.png`.

The two spikes are written up below rather than numbered, because neither lands code.
Until either part is built, the city on macOS or on a Wayland session without `DISPLAY` says in the panel that the desktop has no way to register a shortcut, with the fallback.

## The macOS spike

**Verdict: registering is buildable without cgo, and coming forward is the open question, which only a Mac can answer.**
Nothing in the working arrangement runs macOS (item 80), so this spike is reading plus a build, and no run.

- **Registering works without a permission prompt.**
  Carbon's `RegisterEventHotKey` needs no Accessibility permission, and its events arrive through `InstallEventHandler` on the application's event target, on the main thread's run loop, which Ebitengine already runs.
- **It builds with `CGO_ENABLED=0`.**
  A 60-line program binding `GetApplicationEventTarget`, `InstallEventHandler`, `RegisterEventHotKey`, `UnregisterEventHotKey` and `SetFrontProcessWithOptions` through `purego`, with a `purego.NewCallback` handler and `NSApplication activate` through `purego/objc`, cross-compiled for darwin/arm64 and darwin/amd64 on 2026-10-16.
  That proves the build only: `purego` checks a struct passed by value, as `EventHotKeyID` is, when it is registered at run time.
- **macOS 15 refuses some combinations.**
  Sequoia required a modifier other than Shift or Option, failing with `-9868`; 15.2 relaxed that, and reports since say it comes back.
  So the setting on macOS should refuse an Option- or Shift-only combination before saving, in words.
- **Coming forward is a request since macOS 14, not a command.**
  `NSApplication.activate()` asks, and the system decides from what the user is doing; `activateIgnoringOtherApps` is deprecated, was reported still working on 14, and was reported failing on 26.
  The one reported workaround on Sonoma is Carbon's deprecated `SetFrontProcessWithOptions`.
  Whether a hotkey the application itself received counts as the user asking for it is what is not documented, and it is the whole question.
- **Next step:** run that program on a Mac on macOS 14 or later, press the combination from another application, and see which of `activate()`, `activateIgnoringOtherApps` and `SetFrontProcessWithOptions` brings the window forward.
  It is in this item's session's scratch space and is not committed; it is short enough to write again from the list above.

## The Wayland spike

**Verdict: registering is possible where the desktop's portal backend implements it — GNOME's, KDE's and Hyprland's — and not on wlroots desktops such as Sway; coming forward is untested and has a plausible path.**
This machine runs i3 under X11, with only the GTK portal backend installed, which does not implement `GlobalShortcuts`, so this spike is reading, and no run.

- **Which desktops implement the portal.**
  The GNOME, KDE and Hyprland backends implement `GlobalShortcuts`; `xdg-desktop-portal-wlr` does not, and its request was closed as not planned.
  GNOME asks the user to confirm the first binding; KDE binds without asking and lists the shortcut in System Settings.
- **The app needs an identity.**
  Recent portals (1.21 and later, GNOME 50 and later) refuse an unsandboxed application they cannot resolve to an installed `.desktop` file.
  The packages already install `/usr/share/applications/botropolis.desktop`, but the portal wants a reverse-DNS application ID with a `.desktop` file of the same name, so building this part renames it, to `city.botropolis.Botropolis.desktop` or similar; a binary run from a checkout cannot register at all.
- **The portal decides the combination, not Botropolis.**
  `BindShortcuts` offers a preferred trigger, and the desktop may assign another or let the user change it, so on Wayland the row records a preference and shows what the desktop bound, from `ListShortcuts`.
- **Coming forward.**
  The `Activated` signal carries an `activation_token`, "a token that can be used to activate a window in response to the shortcut getting activated".
  The city is an XWayland window, and that token is an `xdg-activation` token; the likely path is to hand it to the window as its `_NET_STARTUP_ID` and then send `_NET_ACTIVE_WINDOW`, the way X11 applications are activated under Mutter and KWin.
  That is inferred, not tested, and it is the part to try first.
- **It needs D-Bus, which `godbus/dbus` gives without cgo,** and the session bus, which every Wayland desktop with a portal has.
- **Next step:** on a current GNOME or KDE Plasma 6 session, bind a shortcut through the portal from the city, press it from a Wayland-native application, and see whether the token raises the XWayland window.

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
- [What's new in AppKit — WWDC23, on cooperative activation](https://developer.apple.com/videos/play/wwdc2023/10054/)
- [`NSRunningApplication activateWithOptions` does not work on Sonoma — Apple developer forums, with the `SetFrontProcessWithOptions` workaround](https://developer.apple.com/forums/thread/739524)
- [Use macOS cooperative app activation — MacVim issue 1456](https://github.com/macvim-dev/macvim/issues/1456)
- [`activateIgnoringOtherApps` fails on macOS 26 — quadraui issue 1328](https://github.com/JDonaghy/quadraui/issues/1328)
- [`RegisterEventHotKey` with Option and Shift on Sequoia — Apple developer forums](https://developer.apple.com/forums/thread/763878?page=2)
- [Option- and Shift-only shortcuts on Sequoia, updated for 15.2](https://blog.eternalstorms.at/2024/09/23/keyboard-shortcuts-using-option-and-or-shift-modifiers-only-no-longer-allowed-on-macos-sequoia/)
- [XDG Desktop Portal — ArchWiki, the backends' interfaces](https://wiki.archlinux.org/title/XDG_Desktop_Portal)
- [`wayland-global-shortcuts`, on GNOME's confirmation, KDE's silent binding and the `.desktop` requirement](https://github.com/ECRomaneli/wayland-global-shortcuts)
- [Adopt the `GlobalShortcuts` portal — Electron issue 38288, linking the wlroots backend's request](https://github.com/electron/electron/issues/38288)
