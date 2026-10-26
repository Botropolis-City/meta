# 281. A group's line can stand alone with one station and lead nowhere

**Open, in progress since 2026-10-26 in the session "item 281". Filed 2026-10-26 (r1120), from Aria's other laptop on 0.3.2. Nobody's call — a defect.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: some group lines *"don't go anywhere"*.

`placeLines` (`pkg/city/lines.go`) gives a group one station per district holding a member that is drawn, so a group whose drawn members are all in one district has one station and no route, and `pkg/city/lines_test.go` holds that it *should still have a station*.
Since 0.3.2, more groups end that way: hidden scripted runs, sessions whose transcripts are gone, packed sessions and the *Temporary* district take members off the map while the group keeps them (`pkg/state/groups.go` skips missing members), so a line collapses to what is left.

## The fix

A group draws a line only when its drawn members stand in two or more districts; a group in one district shows its badge on its buildings and no line.
Count only members on the map when placing stations, so a group whose other members are hidden does not leave a stub.
Tests: a group in one district draws no line; a group of two districts where one member is hidden draws no line; a group in two drawn districts draws its line; flip `lines_test.go`'s one-district case.
