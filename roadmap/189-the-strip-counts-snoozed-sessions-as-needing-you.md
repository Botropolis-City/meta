# 189. The strip counts snoozed sessions as needing you

**Fixed 2026-10-20 (`a4c2819`, r831). Filed 2026-10-20 (r825), found while working item 184. Nobody's call — a defect.**

Depends on: 184
Landed: slice 1 (`a4c2819`, r831).

[Item 184](184-the-bar-names-a-session-triage-skips.md) makes `botropolis bar` leave out sessions you have marked done or snoozed (through `(*city.Layout).SetAside`), naming the next one waiting and counting the rest as "N set aside".
The city's own top strip, the window title and the state card all read `City().Summary()`, which does not know about the layout: a done session leaves the strip's "N need you" only once it is packed (`d`), and **a snoozed one stays in it until its snooze runs out**. So after item 184 the bar and the strip disagree about snoozed sessions on the same screen.

## The fix

A Scene-level summary that applies `SetAside`, read by the strip, the window title and the state card, so all four surfaces (with the bar) count the same sessions; the strip shows set-aside sessions the way the bar does ("N set aside"), or leaves them out with a reason recorded.

Tests: with one session snoozed and one needing you, the strip, the title and the state card each say "1 needs you", the same as `botropolis bar`; when the snooze runs out, all say "2 need you". A frame of the strip for Aria if its chips change.

## Closed

`Scene.Summary` and `Scene.StateCard` apply `Layout.SetAside`, and the strip, the window title, the needs-you chip's card and the Attention lens read them, so all of them count the same sessions as `botropolis bar` (`a4c2819`, r831).
The strip shows set-aside sessions in a plain "N set aside" chip after the state chips, with no dot and no jump, and the window title ends with it the way the bar's line does.
`pkg/city/scene_summary_test.go` holds the item's tests: one snoozed and one waiting say "1 needs you · 1 set aside" on the headline, list one on the card and count one on the lens; when the snooze runs out they say "2 need you".
`pkg/commands/bar_test.go` checks the bar carries the city's headline for the same snapshot and layout, both before and after the snooze runs out.

Two additions beyond what the item named, both settled with the manager before the tests were written:
the Attention lens panel (item 180) counts the same way, so it agrees with the strip above it,
and clicking the "needs you" chip skips set-aside sessions, so it jumps to the one it counts.
The window title still recomputes only when a snapshot arrives, so a snooze running out shows there at the next update from the daemon, seconds later.

Frame for Aria: [`r831-item-189-strip-set-aside.png`](../botropolis/docs/screenshots/r831-item-189-strip-set-aside.png) (`925d23d`, r834), the hamlet's strip and Attention panel before and after triage snoozes the longest-waiting session.
