# 300. TestPaste presses Ctrl+V on macOS, where paste is Cmd+V, so CI on main is red

**Fixed 2026-10-27 (`9b262e6`, r1181). Filed 2026-10-27 (r1179), from CI on `main`. Nobody's call — a red main, fixed before anything else.**

Since item 290 landed (`7e8aea1`, r1166), both `test-macos` jobs fail on every push, through 0.3.3's candidate `77ae413` (run 40486765643): `TestPaste`'s cases `…/and_Ctrl+V_is_pressed_with_/w/api_on_the_clipboard/it_should_insert_the_clipboard_at_the_caret` and `…/and_the_clipboard_holds_two_lines/it_should_paste_them_as_one_line`, for the finder and New session's fields, *Not equal*.
Item 290 made the paste chord Cmd+V on macOS (`pasteChords(goos)`), and `TestPasteChords` holds that Ctrl+V is not paste there; `TestPaste` still presses Ctrl+V on every platform.

## The fix

`TestPaste` presses the running platform's chord, taken from `pasteChords(runtime.GOOS)`, so it tests the same path a user on that platform hits; nothing in the product changes.
Red first: run the test as darwin would choose its chord (the chord function takes `goos`), then green; and CI's two macOS jobs green on the push.

## Closed

Fixed in two landings, both test-only; nothing in the product changed.
`18dec38` (r1180): `TestPaste` presses `pasteChords(runtime.GOOS)`, and its Shift+Insert case became one case per chord the platform pastes with.
Red first by pressing darwin's chords on Linux, which failed the same two cases per field that CI reported.

**Deviation, flagged for Aria:** that landing's CI (run 40520178576) was still red on both macOS jobs, on `TestQuitPanel`'s *when Ctrl+K is pressed with the panel open*.
It had already failed in run 40486765643 beside `TestPaste`, and this item did not name it.
It is the same fault: the finder opens on `mod+k`, which is Cmd+K on macOS.
At the manager's word it was fixed here too: `9b262e6` (r1181) presses `defaultChords().Open` through a `pressChord` helper that `TestPaste` now shares, red first the same way.
A sweep of `pkg/render`'s tests found no other hard-coded mod chord, since the rest take theirs per platform from `systems`.

CI run 40524170850 on `9b262e6` is green on every job, both `test-macos` jobs included.
