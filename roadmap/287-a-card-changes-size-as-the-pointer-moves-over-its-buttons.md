# 287. A session's card changes size as the pointer moves over its buttons

**Open, in progress since 2026-10-26 in the session "item 287". Filed 2026-10-26 (r1123), from Aria's use of 0.3.2. Nobody's call — Aria said what she wants.**

Aria, 2026-10-26: *"the menus that popup when clicking on a session shouldn't change size depending where I hover. They should always be big enough to show the help text so that the size is static but the content can change. That way it doesn't look like it's flashing"*.

## Why

The pinned card's hint is the description of the button under the pointer (`buttonHint`, `pkg/render/chrome.go`, from `ActionKind.Describe` in `pkg/city/actiontext.go`).
`chrome.go` sets `card.Hint = hint` and then lays the card out with `ui.LayoutCard`, so the card grows when a hint appears, shrinks when it goes, and resizes to each hint's length, every time the pointer crosses a button.

## The fix

Lay the card out once for its content with room for the longest hint among the actions it offers, wrapped to the card's width, and keep that size whatever the pointer is over; the hint row is always there, empty or showing a hint.
The same holds for the hovered card and the strip's state card if they carry hints.
Tests: for a card with several actions, its laid-out rectangle is the same with no hint and with each action's hint; the hint row fits the longest hint without clipping; and a card with no actions has no empty hint row.
