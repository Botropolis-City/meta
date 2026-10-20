# 174. The status bar names the waiting session that comes first alphabetically, not the one waiting longest

**Open, in progress since 2026-10-20 in the session "item 174". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

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
