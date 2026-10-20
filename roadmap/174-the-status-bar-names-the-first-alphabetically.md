# 174. The status bar names the waiting session that comes first alphabetically, not the one waiting longest

**Fixed 2026-10-20 (`a3e91ba`, r787). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

`botropolis bar` puts one waiting session's title on the bar line, and the comment above it says why: *"The bar has room for a name: say who is first in line."*
But `Summarize` (`botropolis/pkg/commands/bar.go`) collects the titles and runs `sort.Strings(needs)` before taking `needs[0]`, so the name is the first in the alphabet.

Against the `metropolis` demo home, staged with `botropolis-demo stage`:

```
$ botropolis bar --format text --home <staged> --socket /nonexistent/b.sock
● 3 needs-you · 12 working · 2 unattended — Crash-safe snapshots
```

*Crash-safe snapshots* has waited 8 minutes; *Modelling triploid varieties* has waited 12.
Triage (`w`) walks the same sessions longest-waiting first, so the bar and the city disagree about who is first.

The fix sorts by how long each has waited, oldest first, as triage does, and keeps the tooltip in the same order.
`bar_test.go` should pin it with two waiting sessions whose alphabetical and waiting orders differ.

## Fixed

`state.LongestWaiting` orders sessions by last activity, oldest first, and breaks ties by ID.
Triage's walk and the bar's `Summarize` both sort with it now, so they can no longer disagree about who is first in line.
The bar line names the first session, and the tooltip lists them in the same order.
`bar_test.go` pins it with two waiting sessions whose alphabetical and waiting orders differ, plus a tie broken by ID, and `order_test.go` pins the comparator itself.
Against the staged `metropolis` home the bar now reads `● 3 needs-you · 12 working · 2 unattended — Modelling triploid varieties`.

Flagged for Aria: the full acceptance suite did not finish before this landed.
The machine was at a load average of 120–195 on 14 cores, and the suite ran past its 40-minute timeout twice without a test failing.
`TestDaemonOfAnotherRelease`'s `events` case hit its 10-second deadline once and passed on a rerun.
The acceptance tests that reach this change — triage and `bar --watch` — pass, and so do the unit and integration tests.
The push went out because the land command piped `make test` through `tail`, which hid its exit code from `&&`.

The bar still counts and names sessions triage has marked done or snoozed, because it never reads the layout; that is item 184.
