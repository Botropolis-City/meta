# 186. Item sessions run full suites side by side and time each other out

**Fixed 2026-10-20 (`2364f77`, r821). Filed 2026-10-20 (r787), from the load of 2026-10-20. Nobody's call — a defect in how items land.**

Depends on: nothing
Landed: slice 1 (`4739efc`, r819).
Landed: slice 2 (`2364f77`, r821).

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

6. **An Xvfb flake under load** (item 178, 2026-10-20): `testing/integration/xvfb` TestStart "when a server is closed, it should stop answering" failed once in an unlocked run and passed twice alone — probably colliding Xvfb displays across parallel suites. Check its display choice holds with two suites at once.

## Closed

**Slice 1** (`4739efc`, r819): points 1–5.
`make land` checks for flock, says when it is waiting, and runs `flock /tmp/botropolis-land.lock make land-under-lock`.
That target fetches, rebases onto `github/main`, runs `LAND_GATE` (default `lint test`) and pushes `HEAD:main`, one line each with nothing piped.
Without flock it fails and names the install on both platforms.
A rebase conflict stops it with the rebase left in progress, for the session to resolve.
`GOLANGCI_LINT_FLAGS` defaults to `--allow-serial-runners`.
Without it, golangci-lint v2.15.0 gives up on its TMPDIR lock after five seconds;
with it, the wait has no limit (`pkg/commands/run.go:497`).
So point 5 was decided for waiting with a shared TMPDIR: every lint on the machine queues, which also keeps the load down.
Unit and integration tests take `TEST_TIMEOUT` (40m), and `ACCEPTANCE_TIMEOUT` defaults to it, so CI's 10m still applies.
Tests: `testing/acceptance/land_test.go` covers two landings at once, a failing gate, a holder killed mid-gate, a rebase conflict, a missing flock and no pipe in the recipe.
`load_test.go` covers every suite's timeout and a lint that waits out a lock held for eight seconds.
The lint test went red with the flag cleared.
Mutating the land recipe (dropping the lock, piping the gate) was refused by the permission check as a gate bypass, so TestLand was seen red only before `make land` existed.

The first landing through `make land` passed its whole gate and then had its push refused, because item 173 pushed twice without the lock during its 25 minutes.
Nothing was harmed, and the second run landed.
`../CLAUDE.md`'s working arrangement now records that the lock holds off only the sessions that take it.

**Slice 2** (`2364f77`, r821): point 6.
Xvfb gives the next server the display number just freed (5 of 5 tries), and `testing/integration/hotkey` started its own Xvfb with no `-auth`, which answers any client.
That open server could take a display the xvfb test had just closed and answer its "it should stop answering" check.
The hotkey test now starts its server through `pkg/xvfb`, with a cookie, and `TestOnlyPkgXvfbStartsXvfb` refuses any exec of Xvfb outside `pkg/xvfb`.
It was red on the hotkey test before the fix.
Two integration suites at once, ten runs each, pass.
The old code did not flake in 20 such runs either, because the window is narrow, so the guard is the check rather than a reproduced failure.

The roadmap-start kickoff now tells every botropolis item to land with `make land` and to run only its own packages while developing (`fd3fa35`).
