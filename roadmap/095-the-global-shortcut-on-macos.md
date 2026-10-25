# 95. The global shortcut on macOS

**Open, in progress since 2026-10-25 in the session "item 95". Filed 2026-10-16 (r499) at Aria's request, from item 84's macOS spike. Nobody's call, but it needs a Mac to run on, and nothing in the working arrangement is one.**

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

## Testing without the hardware

Aria, 2026-10-25: *"I won't suddenly own one of these. We need a vm to test."*
Researched the same day, with nothing installed:
- A macOS VM on this laptop is ruled out by Apple's licence, which allows macOS virtual machines only on Apple-branded hardware (the macOS Sequoia licence, sections 2B(iii) and 2J); OSX-KVM, quickemu's macOS mode and Docker-OSX all break it.
- **GitHub's hosted macOS runners** are free for this public repository, and their image grants Accessibility to `bash` and `osascript` (`configure-tccdb-macos.sh` in `actions/runner-images`). A workflow can bring another app forward, press the combination with `osascript`'s System Events, read the frontmost process and `screencapture` it, once per activation call. Unconfirmed, and the first thing to test: whether a synthetic keystroke fires a Carbon `RegisterEventHotKey` hot key at all.
- If it does not, a cloud Mac rented for its 24-hour minimum (Scaleway's Apple silicon, about €4 for the day) answers it by hand over remote desktop.

## Answered while building

- **Where it runs** (Aria, 2026-10-25, asked by the manager): a GitHub Actions job on the hosted macOS runner, run by `workflow_dispatch` only so it costs no push anything; a rented Mac only if synthetic keys cannot fire the hot key, and that comes back to Aria first.
