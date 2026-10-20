# 186. Item sessions run full suites side by side and time each other out

**Open. Filed 2026-10-20 (r787), from the load of 2026-10-20. Nobody's call — a defect in how items land.**

Depends on: nothing

On 2026-10-20 fourteen item sessions ran on one 14-core machine, and the load average reached 178: each landing ran the full `make lint && make test` at once, the acceptance suite hit its 40-minute limit with no assertion failing, sessions retried, and the load stayed up. Parallel `make lint` runs also failed on golangci-lint's machine-wide lock ("parallel golangci-lint is running").
The manager's stopgap — land one at a time behind `/tmp/botropolis-land.lock` with `flock … sh -c 'git …'` — cannot run from a worktree session (its guard refuses git inside `sh -c`), so sessions improvised holders and scripts; one (item 174) landed with `make test | tail`, whose pipe hid a failing exit code.

## The fix

1. **`make land`** in botropolis: takes the lock itself (`flock`, with a plain message where flock is missing) around fetch, rebase, lint, test and push, with no pipe anywhere in the chain, so a worktree session runs one command and the guard sees no git inside text.
2. **`make lint` defaults `GOLANGCI_LINT_FLAGS=--allow-serial-runners`**, so a second lint waits for the first rather than failing.
3. **The roadmap-start kickoff** tells every item to land with `make land`, and to run only its own packages while developing; `../CLAUDE.md`'s working arrangement says why.

Tests: `make land` in a scratch clone with a fake remote — two at once, the second waits for the first's lock; a failing test stops before push; no pipe in the recipe (the gate's exit code is the push's condition). Two `make lint` at once both pass.

**Two more, from item 167 (2026-10-20):**

4. **`make test-unit` has go test's default 10-minute timeout.** At load ~150 `pkg/render` hit it — the fault item 131 fixed for acceptance. Give the unit and integration targets the same explicit timeout acceptance has.
5. **golangci-lint's parallel-run lock lives in the shared `TMPDIR`**, so a lint inside the land lock still fails while another session lints during development. `TMPDIR=<own dir> make lint` works around it; `--allow-serial-runners` (point 2) makes it wait instead — decide which, and test two lints at once from two worktrees.
