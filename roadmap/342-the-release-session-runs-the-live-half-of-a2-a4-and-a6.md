# 342. The release session runs the live half of A2, A4 and A6

**Open. Filed 2026-11-03 (r1259), at Aria's request during the 0.4.0 run. Nobody's call.**

Aria, 2026-11-03: *"I also think a lot of A1-An could be automated/done by you. Can you try for this run?"*, then *"yes do it"* to this plan.

The [validation checklist](validation-checklist.md) has three tiers.
The scripted checks S1–S10 run in `make test` against a fake `claude` and a fake terminal;
the live checks L1–L2 run against Aria's installed daemon;
and A1–A7 need her real window, terminal or notification.
Three of the A checks do not, in fact, need her:

- **A4**, `! sleep 20` in an attached session reading as working: a real `claude` session under `tmux` in the scratch folder can be typed into, and `botropolis status --json` read while the command runs.
  S9 stages the `shell` record; this is the check that a real `!` writes it, and nothing about it needs a screen.
- **A6**, `botropolis status --live`: a TUI, driven under `tmux` with `send-keys` and read with `capture-pane`, in the scratch folder, with a stopped session to demolish.
- **A2**, hover a district and press `c`: XTEST on a private Xvfb display, the way the recording harness already drives the city, reading the status line and the daemon for the new session.
  The harness refuses `:0` (memory *Capture only a private display*), so this never touches Aria's screen.

A1, A3, A5 and A7 stay Aria's: her terminal opening on `enter`, the real window manager's focus reaching the notifier, her waybar and her tray are what those checks vouch for, and a stand-in for any of them is what S1, S3 and S7 already are.

## What to build

A `make`-reviewed target in botropolis, say `make test-live`, that the release session runs after L1–L2 against the installed package, with one function per check and a one-line pass/fail each, and that refuses `DISPLAY=:0`.
It runs against the real `claude` on the machine and the real installed daemon, so it is not in `make test`.
Add the three as L3–L5 in the checklist's live table, remove them from Aria's, and point `botropolis/RELEASING.md`'s live step at the target.
The first run is the next release's; record it in the checklist's history as the others are.

## Tests

The target's own checks are the tests; unit-test the parsing of `status --json` and of the captured pane where it is more than a string compare, beside the code, BDD-named.
