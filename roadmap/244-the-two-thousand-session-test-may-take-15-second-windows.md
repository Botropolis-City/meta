# 244. The 2,000-session cost test may take 15-second windows, once a quiet machine shows it reads the same

**Open. Filed 2026-10-24 (r1021), split from item 226's last measurement-gated window. Nobody's call — the rule is set; the performance manager measures.**

Depends on: nothing

[Item 226](226-the-acceptance-suite-takes-sixteen-minutes-to-land.md)'s slice 4 shortened the cost tests' streams where a shorter window reads as reliably, test by test, on evidence.
One window was left waiting for a quiet machine: `TestDaemonWithTwoThousandSessions` in `botropolis/testing/acceptance/group_cost_test.go`, whose stream of two 30-second windows would become two of 15 seconds.

**The change, in full** (held as item 226's unpushed `352dae1`, so it is written out here): in `group_cost_test.go`, `stream = 30 * time.Second` becomes `stream = 15 * time.Second`, and the subtest's name *"and one session writes a reply every 200 ms and a prompt every 5 s for two windows of 30 s"* takes the window from `stream` (`fmt.Sprintf("… for two windows of %.0f s", stream.Seconds())`).

**The rule** (item 226, the manager, 2026-10-24): the test's budget is unmet ([item 213](213-the-2000-session-daemon-is-over-its-cpu-budget.md)) and it skips as unmet, so 15 seconds stands only if every one of five interleaved 15-second runs, paired with five at 30, still reads over the 2% and skips as unmet, and both its worst and its median share fall within the 30-second runs' range; each pair starts with the load under 3 over 4 minutes, recorded. Budgets do not move. If the rule fails, the window stays at 30 seconds and this item closes saying so.

The performance manager runs the pairs with `make test-performance RUN='^TestDaemonWithTwoThousandSessions$'` from detached worktrees at exact commits, and a session lands the change through `make land` only if they pass.
