# 189. The strip counts snoozed sessions as needing you

**Open, in progress since 2026-10-20 in the session "item 189". Filed 2026-10-20 (r825), found while working item 184. Nobody's call — a defect.**

Depends on: 184

[Item 184](184-the-bar-names-a-session-triage-skips.md) makes `botropolis bar` leave out sessions you have marked done or snoozed (through `(*city.Layout).SetAside`), naming the next one waiting and counting the rest as "N set aside".
The city's own top strip, the window title and the state card all read `City().Summary()`, which does not know about the layout: a done session leaves the strip's "N need you" only once it is packed (`d`), and **a snoozed one stays in it until its snooze runs out**. So after item 184 the bar and the strip disagree about snoozed sessions on the same screen.

## The fix

A Scene-level summary that applies `SetAside`, read by the strip, the window title and the state card, so all four surfaces (with the bar) count the same sessions; the strip shows set-aside sessions the way the bar does ("N set aside"), or leaves them out with a reason recorded.

Tests: with one session snoozed and one needing you, the strip, the title and the state card each say "1 needs you", the same as `botropolis bar`; when the snooze runs out, all say "2 need you". A frame of the strip for Aria if its chips change.
