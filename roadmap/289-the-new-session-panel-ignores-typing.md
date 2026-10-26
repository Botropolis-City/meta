# 289. The New session panel takes no typed text, only scripted keys

**Open, in progress since 2026-10-26 in the session "item 289". Filed 2026-10-26 (r1123), from item 288's session. Nobody's call — a defect.**

The New session panel's fields — directory, prompt and group name — insert only `g.scriptedRune` (`pkg/render/newsession.go`), the character a scripted run feeds; nothing reads the keyboard there.
The finder reads real typing through a `textinput.Composer` (`pkg/render/overlay.go`), which also handles input methods, and triage's snooze field through `ebiten.AppendInputChars`; the panel has neither.
So typing into New session by hand likely does nothing outside a scripted run, while every test of the panel, being scripted, passes.

## The fix

Give the panel's fields the finder's input path, a `textinput.Composer` per focused field, so plain typing, pasting and input methods all work, and keep the scripted rune for tests.
Look for any other text field that reads only the scripted rune, and give it the same path.
Tests: a field fed through the same seam the finder's tests use receives typed text, a composition, and a commit; switching fields with the arrows sends text to the focused one only; and a guard that every text field in `pkg/render` reads the keyboard, not only the scripted rune.
Confirm by hand in the real app before and after: a frame for Aria is not needed, but the item's close says it was tried.
