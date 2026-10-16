# 95. The global shortcut on macOS

**Open. Filed 2026-10-16 (r499) at Aria's request, from item 84's macOS spike. Nobody's call, but it needs a Mac to run on, and nothing in the working arrangement is one.**

Item 84 built the global shortcut for X11 and wrote up a spike for macOS, which could only read and build, not run: see [item 84](084-a-global-shortcut-off-by-default.md#the-macos-spike).
Until this lands, the settings row on macOS says the desktop has no way to register a shortcut, with the fallback.

What the spike settled:

- Registering works through Carbon's `RegisterEventHotKey` via `purego`, with no cgo, and a test program cross-compiles for arm64 and amd64.
- macOS 15 refuses Option-only and Shift-only combinations, so the row refuses them before saving, in words.

What is open, and is this item's first step: **coming forward**.
Since macOS 14, activating an application is a request the system may refuse.
Run the spike's program on a Mac on macOS 14 or later, press the combination from another application, and see which of `activate()`, `activateIgnoringOtherApps` and `SetFrontProcessWithOptions` brings the window forward.
Then build it behind `pkg/hotkey`'s seam, beside the X11 backend, with the same tests the X11 part has where a Mac runner can run them.

Done when the shortcut opens the finder and brings the window forward on a Mac, the refusal of Option- and Shift-only combinations is tested, and Aria has judged a frame of the row on macOS.
