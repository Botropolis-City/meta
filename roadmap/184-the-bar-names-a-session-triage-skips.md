# 184. The status bar names and counts sessions that triage has marked done or snoozed

**Open. Filed 2026-10-20 (r786), while working item 174. Nobody's call — a defect.**

`botropolis bar` counts every live needs-you session and names the one that has waited longest (`Summarize`, `botropolis/pkg/commands/bar.go`).
Triage leaves two kinds of needs-you session out of its walk (`inTriage`, `botropolis/pkg/city/triage.go`):
one marked done with `d` that has not moved since (`Layout.Done`),
and one snoozed until a time that has not come yet (`Layout.Snoozed`).
The city's footer takes its needs-you line from the same walk (`botropolis/pkg/render/chrome.go`), so it names the walk's first session and says "+N more" from the walk's length.

The bar never reads the layout, so after you mark the longest-waiting session done or snooze it, the city's footer moves on to the next session and the bar keeps naming the one you set aside.
Its "N needs-you" count and its tooltip still include it as well.
Item 174 gave both the same order (`state.LongestWaiting`), but the bar still uses a different set of sessions.

The layout is a file the city writes, `city.LayoutPath()`, read by `city.LoadLayout`, so the bar can read it too.
A fix would pull the done-and-snoozed test out of `inTriage` into a function that takes a layout and a time, and use it from triage and from `Summarize`.
Watch mode would read the layout again on every snapshot, so a snooze that runs out shows up on the bar's next line.
The count probably follows the walk, as the footer's "+N more" does; the item that fixes this should say so in its test tree.
`bar_test.go` should pin it with a done session and a snoozed one that would otherwise be named first.

**Also in the bar** (found by item 171, 2026-10-20): `botropolis bar` prints its counts with the raw state name (`fmt.Sprintf("%d %s", c.N, c.State)` in `botropolis/pkg/commands/bar.go`), so it reads "2 needs-you · 1 working" where the city says "2 need you"; route it through `city.CountLabel` with the rest of this item.
