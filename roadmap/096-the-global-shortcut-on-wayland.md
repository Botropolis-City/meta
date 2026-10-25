# 96. The global shortcut on Wayland

**Open. Filed 2026-10-16 (r499) at Aria's request, from item 84's Wayland spike. Nobody's call, but it needs a GNOME or KDE Plasma 6 session to run on, and this machine is i3 on X11.**

Depends on: 245

Item 84 built the global shortcut for X11 and wrote up a spike for Wayland, which could not run here: see [item 84](084-a-global-shortcut-off-by-default.md#the-wayland-spike).
Until this lands, a Wayland session without `DISPLAY` says the desktop has no way to register a shortcut, with the fallback; with XWayland's `DISPLAY`, an X11 grab sees only X11 clients' keys.

What the spike settled:

- The desktop portal's `GlobalShortcuts` interface works on GNOME, KDE and Hyprland, and not on wlroots desktops such as Sway; `godbus/dbus` reaches it without cgo.
- The portal needs a reverse-DNS application id with a matching `.desktop` file, which Botropolis does not have yet, so this item gives it one and installs it with the packages.
- The desktop may bind a different trigger from the one asked for, so on Wayland the row records a preference and shows what the desktop bound.

What is open, and is this item's first step: **coming forward**.
The city is an XWayland window; the likely path is to hand the portal's `activation_token` to it as `_NET_STARTUP_ID` and then send `_NET_ACTIVE_WINDOW`.
On a GNOME or KDE Plasma 6 session, bind a shortcut through the portal from the city, press it from a Wayland-native application, and see whether the window comes forward.

Done when the shortcut opens the finder and brings the window forward on GNOME and on KDE, Sway says it has no way to register one, and Aria has judged a frame of the row there.

## Testing without the hardware

Aria, 2026-10-25: *"I won't suddenly own one of these. We need a vm to test."*
Researched the same day, with nothing installed:
- **Two libvirt guests on this machine**, Fedora Workstation (GNOME 48 or later, the first with the portal's GlobalShortcuts backend) and Fedora KDE Plasma, from `qemu-desktop`, `libvirt`, `virt-manager` and `edk2-ovmf`, all in Arch's `extra` repository. Keys go in from the host with `virsh send-key`, below the compositor, and frames come out with `virsh screenshot`; plain virtio-gpu is enough, since activation does not need 3D.
- `BindShortcuts` shows a confirmation dialog on both desktops, on every launch on GNOME 48; both are keyboard-navigable, so the script accepts it with keys.
- Sway needs no VM: its portal (`xdg-desktop-portal-wlr`) offers no GlobalShortcuts, and a nested Sway on the host confirms the refusal.
- Whether GNOME's and KDE's backends fill in the `Activated` signal's `activation_token` is part of what this item finds out.
