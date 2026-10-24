# 226. The acceptance suite takes sixteen minutes on every landing

**Open, in progress since 2026-10-24 in the session "item 226". Filed 2026-10-24 (r968) at Aria's request, and prioritised by her: start it before other ready items. Nobody's call — the shape is agreed below.**

Aria, 2026-10-24: *"can you tell me why our acceptance tests take so long? is there a way to speed them up? Do we always need to run all of them? Can we chunk and cache in some form based on what changed?"*, then *"Add a roadmap item for this, and let's prioritize it"*.

**What it costs.** `make land` ([item 186](186-item-sessions-land-side-by-side-and-time-out.md)) runs the full `make lint && make test` inside the landing lock, and `go test ./testing/acceptance/...` took 957 s of it at the 0.3.0 release, on a quiet machine. Every item landing pays it, one at a time, so with several sessions the queue for the lock is the bottleneck: item 217's one-line changelog commit waited behind item 162's landing and then ran the whole suite again.

**Why it is slow** (from reading `botropolis/testing/acceptance/`, no per-test timings yet):
- It is one Go package of 74 files and 88 top-level tests, so they run one after another: only 6 files call `t.Parallel()`.
- About a dozen tests measure cost over wall-clock windows on purpose: streams of 15, 30 and 65 s (`daemon_cost_test.go`, `hidden_cost_test.go`, `group_cost_test.go`), settles of up to 3 minutes, `memory_test.go`'s 20 s + 5 s, and fixed `time.Sleep`s in `dashboard_test.go`, `state_test.go` and `owndaemon_test.go`.
- Every test drives real binaries (a city, a daemon, often Xvfb) in an isolated home.
- Load stretches all of it: 40 minutes when fourteen sessions landed at once.

**What already exists.** [Item 117](117-acceptance-tests-cached-past-code-changes.md) built `make test-acceptance-map` and `make test-acceptance-changed` (`botropolis/tools/acceptance-targets`): a coverage map from each acceptance test to the packages it executes, and a runner that runs only the tests a change can reach, falling back to a full run that says why. Nothing calls it: the map lives in each checkout's `.cache/`, so every item worktree starts without one, and `land-under-lock` runs the full `make test`.
CI runs the full suite on every push to `main`, and `make land` already refuses to land while `main` is red (`tools/ci-status`), so a full suite does run on every commit; the local full run is a second copy of that check, and the expensive one.

## The fix

1. **Measure.** One run of the suite with `go test -json` on a quiet machine, giving every test's time; write the table into this item, sorted. Every later slice states its saving against it.
2. **Two tiers.** Behaviour tests call `t.Parallel()` (each already has its own home; fix any that share a port, a lock or a fixed path). Cost tests, which measure CPU and memory and need a quiet machine, stay serial, by a build tag or name prefix the runner understands, and run after the behaviour tier.
3. **Land on what changed.** `make land` runs `test-acceptance-changed` instead of the full acceptance suite. The map is shared by every checkout and worktree, for example under `${XDG_CACHE_HOME:-~/.cache}/botropolis/acceptance-map/`, keyed by the commit it was made at, and `changed` diffs against that commit. A change it cannot map (a new test, `go.mod`, `testing/helpers`, the Makefile, a missing map) falls back to the full suite and says why, as it does now. CI keeps the full suite on every push, and the red-`main` check stays the backstop. CI refreshes the map on `main` (as a run artifact or a cache), or the first full local run does.
4. **Shorter waits.** Replace each fixed `time.Sleep` with a wait on the event it stands for, and shorten the cost tests' streams where counting instructions ([item 209](209-cost-gates-fail-landings-on-a-busy-machine.md)) makes a shorter window as reliable; [item 225](225-testthreadcpu-fails-under-load.md) is the same shape for one unit test.

Considered and not chosen: dropping acceptance from `make land` altogether and relying on CI after the push. It is fastest, but with many sessions landing, one bad push blocks every landing until it is fixed.

Tests: the runner's selection is already tested in `tools/acceptance-targets/targets`; add a test that a worktree with no map of its own uses the shared one, and that a change to a cost test's package selects it. The goal, against slice 1's table: a typical one-package item landing in under 10 minutes, the full suite under 8.
