# 290. No text field in the city takes a paste

**Fixed 2026-10-27 (`7e8aea1`, r1166). Filed 2026-10-26 (r1124), from item 289's session. Nobody's call — a defect.**

Depends on: 289, 284

Ctrl+V does nothing in any of the city's text fields: the finder, New session's directory, prompt and group name, triage's snooze, and item 288's new group name.
Ebitengine's `textinput.Composer`, which they read the keyboard through (item 289), has no clipboard support, and nothing else reads the clipboard into a field.
A directory or a prompt is exactly what someone pastes.

## The fix

1. Ctrl+V (Cmd+V on macOS), and Shift+Insert on Linux, paste the clipboard's text into the focused field at the caret, with newlines in a one-line field turned to spaces.
2. Read the clipboard through the same desktop tools the city copies with (`pkg/control/desktop.go`: `wl-paste`, `xclip -o -selection clipboard`, `xsel --clipboard --output`, `pbpaste`), and **under item 284's rules**: beside the loop, with a deadline, no wait on a pipe a child can hold, and no inherited descriptors, so a paste can never freeze the map as copying did.
3. Every field gets it through one place, held by item 289's guard.
4. Tests: a paste reaches the focused field only; a clipboard tool that never exits returns at its deadline with a notice and the field unchanged; a multi-line paste into a one-line field becomes one line; no clipboard tool installed says so.

## Answered while building

- **A scripted city never reads the clipboard** (manager, 2026-10-26): a screenshot, a film, a `--keys` run or a clip's script is given no clipboard, so whatever Aria last copied cannot end up in a published frame. A paste there says "pasting is not available here". A driven city has none either.

## Closed

Fixed in `7e8aea1` (r1166).

1. Ctrl+V and Shift+Insert on Linux, and Cmd+V on macOS, paste at the caret. The text becomes one line: a trailing newline is dropped, other line breaks and tabs become spaces, and other control characters go.
2. `Control.Paste` reads through `wl-paste --no-newline --type text`, `xclip -o -selection clipboard`, `xsel --clipboard --output` or `pbpaste`, under copy's two-second deadline. `execRunner.Read` follows item 284: its output goes to files, never a pipe a forked child can hold, with a wait delay and no inherited descriptors.
3. Every field takes a paste through `g.pasted`, which reads the clipboard beside the loop. The text goes only to the panel that asked; one read runs at a time; a failure becomes a notice and leaves the field unchanged. Item 289's guard now also fails for any field that no function calling `g.pasted` touches.
4. Tests: `pkg/control/paste_test.go` covers each tool, no tool installed, the deadline, a tool that never answers and an empty clipboard. `pkg/control/exec_test.go` runs real processes through `Read`: output, a forked child holding stdout, a tool that never exits, an error on stderr, and descriptor leaks. `pkg/render/paste_test.go` covers all six fields, a multi-line paste, the focused field only, Shift+Insert, a hung tool, a second press, a panel closed mid-paste, and a scripted city reading nothing. Each was confirmed red by mutation: delivery to any panel, a second read, a read on the loop, and a field with no paste.

Tried against real xclip on an Xvfb display: `Control.Paste` read a two-line selection in 6 ms.
For Aria: no keys could be sent into a real window, because this machine has no xdotool, so Ctrl+V in the open city is tested only through the scripted keys. Wayland's `wl-paste` and macOS's `pbpaste` are tested only against a fake runner.
