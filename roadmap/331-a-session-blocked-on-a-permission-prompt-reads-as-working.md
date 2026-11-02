# 331. A background session blocked on a permission prompt reads as working, not needs-you

**Open, in progress since 2026-11-03 in the session "item 331". Filed 2026-11-03 (r1228), from 0.3.5's L1 check against Aria's live daemon. Nobody's call — a defect; whether it gates 0.3.5 was Aria's.**

L1 (the live-state check, 14 live sessions in one pass) found one disagreement: a background session whose Claude Code record says *waiting*, `waitingFor: "permission prompt"`, last updated 8 hours before, whose transcript ends in a `tool_use` with no result, and which `claude agents` calls *blocked*, read as **working** in Botropolis.
A permission prompt is the clearest case of needing you, and the city said the opposite for eight hours.
The same reading is in 0.3.4, since nothing in 0.3.5 touched it.

## The fix

The daemon reads the CLI record's `waitingFor` (S9's rule already makes a shell command read as working; a permission prompt is the other way round) and a `tool_use` with no result past a short grace reads as needs-you, not working.
Tests in `pkg/state` and `pkg/daemon` for the record, and an acceptance case staging that transcript; L1 re-run against the next release.
