# 281. A group's line can stand alone with one station and lead nowhere

**Fixed 2026-10-26 (`9dbf8cc`, r1133). Filed 2026-10-26 (r1120), from Aria's other laptop on 0.3.2. Nobody's call — a defect.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: some group lines *"don't go anywhere"*.

`placeLines` (`pkg/city/lines.go`) gives a group one station per district holding a member that is drawn, so a group whose drawn members are all in one district has one station and no route, and `pkg/city/lines_test.go` holds that it *should still have a station*.
Since 0.3.2, more groups end that way: hidden scripted runs, sessions whose transcripts are gone, packed sessions and the *Temporary* district take members off the map while the group keeps them (`pkg/state/groups.go` skips missing members), so a line collapses to what is left.

## The fix

A group draws a line only when its stations stand in two or more drawn districts; a group in one district shows its badge on its buildings and no line.
Count only members on the map when placing stations, so a group whose other members are hidden does not leave a stub.
Tests: a group in one district draws no line; a group of two districts where one member is hidden draws no line; a group in two drawn districts draws its line; flip `lines_test.go`'s one-district case.

## Answered while building

- **The rule** (manager, 2026-10-26): a group draws a line when its stations — its members' districts and the districts its coordinator's subagents worked in, never the depot — stand in two or more drawn districts; packed members make no station. The coordinator is not changed, so a group whose members stand in one district draws no line even if subagents worked elsewhere.

## Closed

Fixed in `9dbf8cc` (r1133), with a changelog entry under 0.3.3's *Fixed*.
`placeLines` never makes a station at the depot, so a packed member no longer pulls a line out to it.
A new `Line.Leads` says whether a line's stations stand in two districts or more, and `Scene.Lines`, which the drawing and the City Plan read, returns only those, so a one-district line is not drawn and its buildings carry no "station N of M".
Hidden projects and scripted runs were already off the map before stations are placed, so they needed no change.
`pkg/city/lines_test.go` holds the four approved cases: one district, two with one hidden, two with one packed, and two drawn districts.

Flagged for Aria, two deviations:

- **The line is still computed, just not drawn.** Removing it from the city emptied the stand-up copy, the dive and the finder's route of a one-district group, which read the line as the group's data (`TestStandup` and `TestKinds` went red), so those keep working and only the map loses the stub.
- **A one-district group's subagent visits make no line.** The coordinator is chosen only among sessions that reach another member district, so such a group never has one; the manager kept the coordinator as it is rather than widen a defect fix.
