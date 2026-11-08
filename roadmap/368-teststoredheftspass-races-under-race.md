# 368. `TestStoredHeftsPass` has a data race that only `-race` sees

**Open, in progress since 2026-11-07 in the session "item 368". Filed 2026-11-07 (r1334), found by item 365's session and reproduced by the roadmap manager. Nobody's call — a defect, in the test or the code. It ships in 0.5.1, at Aria's request.**

`go test -race -run TestStoredHeftsPass ./pkg/state/` reports `DATA RACE` on its own, in the case *"when a load applies the hefts while a pass moves one"*.
The gate (`make test`) does not run `-race`, so nothing has caught it.

## Where it stands

Both racing accesses are `pace.start` (`pkg/state/pace.go:36`), which writes `p.since` from `storedHefts.pass` (`pkg/state/storedheft.go:162`).
One goroutine is the test's own loop: `passOf` in `storedheft_internal_test.go` (line 53) sets `h.running = true` and calls `pass` itself, without checking that no pass is running.
The other is a pass that `apply` starts through `start` (`storedheft.go:120` and `:146`), once the test's pass has cleared `running`.
So two passes can run at once. In the app, `start` allows only one; in this test, the hand-run passes bypass that check.

## The fix

First decide whether only the test can run two passes at once, or the code can too.
If only the test, make `passOf` take the same guard as `start`.
If the code can, make `pace` safe for that, or keep `running` held until `pass` has returned.
Then consider whether `make test` should run `pkg/state` under `-race`, so a race in its goroutines fails the gate. Measure what that costs first.

## Answered while building

- **Only the test can race** (item 368's session, 2026-11-07): in the app, `start` is the only caller of `pass`, and it checks and sets `running` under `h.mu`, so a new pass happens-after the last one. The test's `passOf` set `running` regardless, while a pass `apply` had started was still running.
  A full `go test -race ./pkg/state/` reports this one race and nothing else.
- **The fix is test-only** (roadmap manager, 2026-11-07): approved. `passOf` takes the same guard as `start`, and the subtest drops its own `h.running = true`. The test tree is unchanged, and the red is `-race -count=20`.
- **`-race` runs in CI, not in `make land`** (roadmap manager, 2026-11-07). On `pkg/state` it costs 3–7× (11.8 s plain against 33.1 s under race, measured at load 38), about 20–30 s on every landing for one package.
  So CI runs `go test -race ./pkg/state/` as a step of its own, where it holds no landing lock, and a race there turns `main` red, which is fixed first. The local gate is unchanged.
