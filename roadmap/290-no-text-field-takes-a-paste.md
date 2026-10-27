# 290. No text field in the city takes a paste

**Open, in progress since 2026-10-26 in the session "item 290". Filed 2026-10-26 (r1124), from item 289's session. Nobody's call — a defect.**

Depends on: 289, 284

Ctrl+V does nothing in any of the city's text fields: the finder, New session's directory, prompt and group name, triage's snooze, and item 288's new group name.
Ebitengine's `textinput.Composer`, which they read the keyboard through (item 289), has no clipboard support, and nothing else reads the clipboard into a field.
A directory or a prompt is exactly what someone pastes.

## The fix

1. Ctrl+V (Cmd+V on macOS), and Shift+Insert on Linux, paste the clipboard's text into the focused field at the caret, with newlines in a one-line field turned to spaces.
2. Read the clipboard through the same desktop tools the city copies with (`pkg/control/desktop.go`: `wl-paste`, `xclip -o -selection clipboard`, `xsel --clipboard --output`, `pbpaste`), and **under item 284's rules**: beside the loop, with a deadline, no wait on a pipe a child can hold, and no inherited descriptors, so a paste can never freeze the map as copying did.
3. Every field gets it through one place, held by item 289's guard.
4. Tests: a paste reaches the focused field only; a clipboard tool that never exits returns at its deadline with a notice and the field unchanged; a multi-line paste into a one-line field becomes one line; no clipboard tool installed says so.
