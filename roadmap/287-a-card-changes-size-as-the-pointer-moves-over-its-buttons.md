# 287. A session's card changes size as the pointer moves over its buttons

**Fixed 2026-10-26 (`aac34c6`, r1140). Filed 2026-10-26 (r1123), from Aria's use of 0.3.2. Nobody's call — Aria said what she wants.**

Aria, 2026-10-26: *"the menus that popup when clicking on a session shouldn't change size depending where I hover. They should always be big enough to show the help text so that the size is static but the content can change. That way it doesn't look like it's flashing"*.

## Why

The pinned card's hint is the description of the button under the pointer (`buttonHint`, `pkg/render/chrome.go`, from `ActionKind.Describe` in `pkg/city/actiontext.go`).
`chrome.go` sets `card.Hint = hint` and then lays the card out with `ui.LayoutCard`, so the card grows when a hint appears, shrinks when it goes, and resizes to each hint's length, every time the pointer crosses a button.

## The fix

Lay the card out once for its content with room for the longest hint among the actions it offers, wrapped to the card's width, and keep that size whatever the pointer is over; the hint row is always there, empty or showing a hint.
The same holds for the hovered card and the strip's state card if they carry hints.
Tests: for a card with several actions, its laid-out rectangle is the same with no hint and with each action's hint; the hint row fits the longest hint without clipping; and a card with no actions has no empty hint row.

## Closed

The pinned card now carries every action's hint (`city.Card.Hints`, filled by `SelectedCard`), and `ui.LayoutCard` keeps as many small lines as the longest of them wraps to at the card's own width, whatever the pointer is over; the hovered hint fills those lines, so a hint never widens or resizes the card (`aac34c6`, r1140).
`TestLayoutCardFace` holds it: the laid-out rect is the same with no hint and with each action's hint, data-driven over the hints; the longest wraps inside the card, whole; and a card with no actions keeps no hint row.
The hovered and strip state cards carry no actions, so they have no hint row.

The first landing failed `TestSidebarCard`: the sidebar's docked card has never been handed a hint, and the reserved rows made its compact form too tall to dock in a 600-tall window.
It carries no hints, as before (`47c8367`, r1141).
Flagged for Aria: with the sidebar open, the selected session's card still shows no hint under its buttons, as it never has; if it should, that is a new item.
