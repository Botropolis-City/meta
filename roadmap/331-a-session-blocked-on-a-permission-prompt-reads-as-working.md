# 331. A background session blocked on a permission prompt reads as working, not needs-you

**Fixed 2026-11-02 (`d1a78d4`, r1229). Filed 2026-11-03 (r1228), from 0.3.5's L1 check against Aria's live daemon. Nobody's call — a defect; whether it gates 0.3.5 was Aria's.**

Depends on: nothing
Landed: slice 1 (`d1a78d4`, r1229).

L1 (the live-state check, 14 live sessions in one pass) found one disagreement: a background session whose Claude Code record says *waiting*, `waitingFor: "permission prompt"`, last updated 8 hours before, whose transcript ends in a `tool_use` with no result, and which `claude agents` calls *blocked*, read as **working** in Botropolis.
A permission prompt is the clearest case of needing you, and the city said the opposite for eight hours.
The same reading is in 0.3.4, since nothing in 0.3.5 touched it.

## The fix

The daemon reads the CLI record's `waitingFor` (S9's rule already makes a shell command read as working; a permission prompt is the other way round) and a `tool_use` with no result past a short grace reads as needs-you, not working.
Tests in `pkg/state` and `pkg/daemon` for the record, and an acceptance case staging that transcript; L1 re-run against the next release.

## Fixed

The CLI's record says `waiting`, with `waitingFor` naming a permission prompt or a question, while a session is stopped on a person.
`derive()` did not know the word and fell through to busy, so the session read as working, or unattended in the background.
A `waiting` record now reads as needs-you, and a hook overlay that says working yields to it until the record changes, the mirror of item 250's yield to `shell`.

Tests: `pkg/claude` reads `waitingFor`; `pkg/state`'s `TestRecordStatus` covers a background record waiting on a permission prompt with a tool call in flight, and an interactive one waiting on input;
`pkg/daemon`'s `TestDaemon` sends a PreToolUse to a waiting session, which still needs you, and then turns the record busy.
`testing/acceptance/waiting_test.go` runs botropolisd over a staged home with this item's case, a background record waiting on a permission prompt eight hours old over an unanswered `tool_use`, beside a busy control, and was red with the fix removed.

Deviation, agreed with the roadmap manager: a `tool_use` with no result past a grace is **not** read as needs-you on its own, because a long foreground command looks the same; the record is the authoritative word.
L1 is still to be re-run against the next release.
