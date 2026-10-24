# 226. The acceptance suite takes sixteen minutes on every landing

**Open, in progress since 2026-10-24 in the session "item 226". Filed 2026-10-24 (r968) at Aria's request, and prioritised by her: start it before other ready items. Nobody's call — the shape is agreed below.**

Depends on: nothing
Landed: slice 1 (`0922f2b`, r969).
Landed: slice 2 (`8c2b968`, r996).
Landed: slice 3 (`eebf342`, r1002).

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

## Slice 1: what each test costs

Measured 2026-10-24 at r969 (`1ba9d96`), with `go test -count=1 -json -timeout 40m ./testing/acceptance/...` on a quiet machine: no other item session running, 14 cores, load average 2.7 at the start and 4.1 at the end.
The build cache was warm, so building the binary in `TestMain` took 2.5 s of it.

**Wall time: 800 s**, against 957 s at the 0.3.0 release.
The 87 top-level tests add up to 752 s, so the suite is serial in all but name: the three tests that call `t.Parallel()` at the top level ran together in the last 8.4 s.
`TestToolchainPins` failed, and nothing in this item caused it: the machine's own Go is now 1.27.3 while the pin is 1.27.2, and its `GOTOOLCHAIN=local` case expects the version that ran to be the pin.

- **The cost tier is 349 s, 46%**: the seven tests that measure CPU or memory (`hidden_cost_test.go`, `daemon_cost_test.go`, `group_cost_test.go`, `memory_test.go`).
  The top three are 289 s by themselves.
- **The behaviour tier is 403 s**, and no behaviour test takes more than 43 s, so run in parallel it is bounded by its longest test and by the load the others make.
- **So two tiers alone should bring the full suite to roughly 349 s plus a minute or two**, about 7 to 8 minutes, before slice 4 shortens the cost tier's streams.
- 66 of the 87 tests take under 2 s each, and the 21 that remain are 95% of the time.

| # | test | seconds | share | cumulative | tier |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | `TestAnUnwatchedCityUnderAStreamOfSnapshots` | 130.1 | 17.3% | 17% | cost |
| 2 | `TestSettledDaemonUnderAStreamOfChanges` | 80.5 | 10.7% | 28% | cost |
| 3 | `TestDaemonWithTwoThousandSessions` | 78.4 | 10.4% | 38% | cost |
| 4 | `TestTheCacheSeesTheBinary` | 42.8 | 5.7% | 44% | behaviour |
| 5 | `TestTargetedRuns` | 36.9 | 4.9% | 49% | behaviour |
| 6 | `TestDaemonUnderAStreamOfChanges` | 36.1 | 4.8% | 54% | cost |
| 7 | `TestScriptsAreInTheCacheKey` | 33.7 | 4.5% | 58% | behaviour |
| 8 | `TestFirstLaunchLoad` | 33.2 | 4.4% | 63% | behaviour |
| 9 | `TestLintChecksFormatting` | 26.9 | 3.6% | 66% | behaviour |
| 10 | `TestFrameRunsKeepTheirOwnState` | 26.6 | 3.5% | 70% | behaviour |
| 11 | `TestAnUnfocusedCityUnderAStreamOfChanges` | 24.1 | 3.2% | 73% | behaviour |
| 12 | `TestBuildingLooksCached` | 23.2 | 3.1% | 76% | behaviour |
| 13 | `TestSettledMemory` | 20.3 | 2.7% | 79% | cost |
| 14 | `TestFirstLaunchCityWaiting` | 18.0 | 2.4% | 81% | behaviour |
| 15 | `TestFirstLaunchResumes` | 14.9 | 2.0% | 83% | behaviour |
| 16 | `TestFirstLaunch` | 14.6 | 1.9% | 85% | behaviour |
| 17 | `TestTheStreamOnABusyCity` | 12.3 | 1.6% | 87% | behaviour |
| 18 | `TestSharingClip` | 9.5 | 1.3% | 88% | behaviour |
| 19 | `TestFirstLaunchCity` | 9.2 | 1.2% | 89% | behaviour |
| 20 | `TestLand` | 8.4 | 1.1% | 90% | behaviour |
| 21 | `TestLintWaitsForLint` | 8.4 | 1.1% | 92% | behaviour |
| 22 | `TestSharingGIF` | 7.6 | 1.0% | 93% | behaviour |
| 23 | `TestBuildingSheetLights` | 7.3 | 1.0% | 93% | behaviour |
| 24 | `TestCityScreenshot` | 5.8 | 0.8% | 94% | behaviour |
| 25 | `TestHeadlessCitiesStartedTogether` | 4.4 | 0.6% | 95% | behaviour |
| 26 | `TestRecordedClipKeepsTheScenesTime` | 3.5 | 0.5% | 95% | behaviour |
| 27 | `TestStartUpPeak` | 2.8 | 0.4% | 96% | cost |
| 28 | `TestSharingPicture` | 2.7 | 0.4% | 96% | behaviour |
| 29 | `TestCheckPublishable` | 2.7 | 0.4% | 96% | behaviour |
| 30 | `TestReleaseBuildHasNoFrameTooling` | 2.6 | 0.3% | 97% | behaviour |
| 31 | `TestSidebarScrolls` | 2.5 | 0.3% | 97% | behaviour |
| 32 | `TestTheStillCityMatchesTheCityDrawnDirectly` | 2.2 | 0.3% | 97% | behaviour |
| 33 | `TestAnswerAndComeBack` | 2.0 | 0.3% | 98% | behaviour |
| 34 | `TestFindByThreeWords` | 1.7 | 0.2% | 98% | behaviour |
| 35 | `TestManPages` | 1.6 | 0.2% | 98% | behaviour |
| 36 | `TestStartASessionAnywhere` | 1.3 | 0.2% | 98% | behaviour |
| 37 | `TestReopenLastFriday` | 1.3 | 0.2% | 98% | behaviour |
| 38 | `TestLensKeys` | 0.9 | 0.1% | 99% | behaviour |
| 39 | `TestDrive` | 0.9 | 0.1% | 99% | behaviour |
| 40 | `TestCityAgainstAnotherRelease` | 0.9 | 0.1% | 99% | behaviour |
| 41 | `TestKeyList` | 0.8 | 0.1% | 99% | behaviour |
| 42 | `TestSidebarCard` | 0.7 | 0.1% | 99% | behaviour |
| 43 | `TestGroupingCostPerPrompt` | 0.6 | 0.1% | 99% | cost |
| 44 | `TestCheckAntialias` | 0.6 | 0.1% | 99% | behaviour |
| 45 | `TestDemoScenarios` | 0.5 | 0.1% | 99% | behaviour |
| 46 | `TestWhatEachPieceOfWorkWasDoing` | 0.5 | 0.1% | 99% | behaviour |
| 47 | `TestCheckPackagesLicences` | 0.4 | 0.1% | 99% | behaviour |
| 48 | `TestToolchainPins` | 0.4 | 0.1% | 99% | behaviour, **failed** |
| 49 | `TestDaemonOfAnotherRelease` | 0.4 | 0.1% | 99% | behaviour |
| 50 | `TestAssetSources` | 0.4 | 0.1% | 100% | behaviour |
| 51 | `TestLabelsDoNotOverlap` | 0.4 | 0.0% | 100% | behaviour |
| 52 | `TestPackagesInstallManPages` | 0.2 | 0.0% | 100% | behaviour |
| 53 | `TestExplainAndReference` | 0.2 | 0.0% | 100% | behaviour |
| 54 | `TestLiveTranscriptAppend` | 0.2 | 0.0% | 100% | behaviour |
| 55 | `TestRoadTagsDrawOverTheCity` | 0.2 | 0.0% | 100% | behaviour |
| 56 | `TestJournalAfterAGap` | 0.2 | 0.0% | 100% | behaviour |
| 57 | `TestStatus` | 0.2 | 0.0% | 100% | behaviour |
| 58 | `TestOnlyPkgXvfbStartsXvfb` | 0.2 | 0.0% | 100% | behaviour |
| 59 | `TestNewerLayout` | 0.2 | 0.0% | 100% | behaviour |
| 60 | `TestLabelsHotkey` | 0.1 | 0.0% | 100% | behaviour |
| 61 | `TestStreamColumn` | 0.1 | 0.0% | 100% | behaviour |
| 62 | `TestStreamColumnNarrow` | 0.1 | 0.0% | 100% | behaviour |
| 63 | `TestStreamScrolls` | 0.1 | 0.0% | 100% | behaviour |
| 64 | `TestEveryBuiltBinaryIsInTheCacheKey` | 0.1 | 0.0% | 100% | behaviour |
| 65 | `TestNothingRunsXvfbRun` | 0.1 | 0.0% | 100% | behaviour |
| 66 | `TestOneCity` | 0.1 | 0.0% | 100% | behaviour |
| 67 | `TestTriageWalk` | 0.1 | 0.0% | 100% | behaviour |
| 68 | `TestDemoCorpusIsClean` | 0.1 | 0.0% | 100% | behaviour |
| 69 | `TestFind` | 0.1 | 0.0% | 100% | behaviour |
| 70 | `TestTestTimeouts` | 0.1 | 0.0% | 100% | behaviour |
| 71 | `TestSurface` | 0.1 | 0.0% | 100% | behaviour |
| 72 | `TestReleaseAliases` | 0.1 | 0.0% | 100% | behaviour |
| 73 | `TestScratchModule` | 0.1 | 0.0% | 100% | behaviour |
| 74 | `TestDocumentationStructure` | 0.1 | 0.0% | 100% | behaviour |
| 75 | `TestTheTestBinaryLinksTheBinary` | 0.0 | 0.0% | 100% | behaviour |
| 76 | `TestCalibrateCoreRate` | 0.0 | 0.0% | 100% | behaviour, skipped |
| 77 | `TestReadmeCredits` | 0.0 | 0.0% | 100% | behaviour |
| 78 | `TestTheWorkAFrameTakes` | 0.0 | 0.0% | 100% | behaviour |
| 79 | `TestTheLooksAFrameKeeps` | 0.0 | 0.0% | 100% | behaviour |
| 80 | `TestTheStillLayerAFrameKeeps` | 0.0 | 0.0% | 100% | behaviour |
| 81 | `TestStartUnderSignals` | 0.0 | 0.0% | 100% | behaviour, skipped |
| 82 | `TestHomeIsolation` | 0.0 | 0.0% | 100% | behaviour |
| 83 | `TestReadmeNamesRealVariables` | 0.0 | 0.0% | 100% | behaviour |
| 84 | `TestTheTestBinaryLinksTheTargetsTool` | 0.0 | 0.0% | 100% | behaviour |
| 85 | `TestTeardownSoak` | 0.0 | 0.0% | 100% | behaviour, skipped |
| 86 | `TestVersionCheckSurface` | 0.0 | 0.0% | 100% | behaviour |
| 87 | `TestCIStatus` | 0.0 | 0.0% | 100% | behaviour |

## Slice 2: three tiers became two, and parallel became processes

**The CPU and memory tests leave the landing gate entirely** (Aria, 2026-10-24, in item 226's session): they run in `make test-performance`, which the performance manager runs on demand and before each release, and which the release workflow runs before it tags.
A test that measures CPU or memory starts with `performanceTier(t)`, which skips unless `BOTROPOLIS_PERFORMANCE=1`.
Every function of the package's own that reads a process's CPU or memory now lives in `testing/acceptance/meters_test.go`.
`TestEveryAcceptanceTestIsInTheTierItNeeds` follows each test through the package's own calls, and fails any test that reaches a meter there or in `pkg/measure` without the marker, or carries the marker without reaching one.
It was mutated red by dropping `TestStartUpPeak`'s marker.

Two tests mixed deterministic checks with a limit in CPU or memory, and were split so first launch stays covered on every landing:
`TestFirstLaunch` (the whole history is read) and `TestFirstLaunchCost` (a core, Private_Dirty);
`TestFirstLaunchLoad` (bytes before the first snapshot, usage held whole, the plant's output) and `TestFirstLaunchLoadCost`;
`TestFirstLaunchCity` (the percentage) and `TestFirstLaunchCityCPU`.
Slice 1's table missed that `TestFirstLaunch*` measured at all; the guard found it.

**`t.Parallel()` was tried and dropped.**
At `-parallel 8` in one process, a city found another test's city "already open", `TestFirstLaunchResumes` read twelve times its limit from another daemon's checkpoint, and two tests' `t.Setenv` panicked: `RunIsolated` gives one home to a whole process, so the daemon and one-city sockets under `XDG_RUNTIME_DIR`, the caches and the checkpoints were shared.
`make test-acceptance` now runs `tools/acceptance-targets run`, which builds the test binary once, lists its tests with `-test.list`, refuses unless that list is exactly the package's Test functions, and runs each one but the performance tier in a process of its own, with the binary built once and named to each through `BOTROPOLIS_ACCEPTANCE_BINARY`.
Each process is its own `TestMain`, so each test has the isolation a whole run had, and `pkg/measure`'s work counters are per process, so the work tier went too.
A failing, panicking, unreported or timed-out test is named with its output, and a run of no tests fails; an end-to-end test builds a fixture package with a passing, a failing and a panicking test and runs it through the real runner.

**How many at once.** `ACCEPTANCE_PARALLEL` defaults to half the cores, at least one and at most six.
Measured at a load of 24 to 50 with other sessions working, not on a quiet machine: 80 tests in 189 s six at a time, and 245 s four at a time, all green at four.
At six, `TestLintChecksFormatting` failed once, on this slice's own mistake (`meters_test.go` lacked the `//go:build linux` of the files its functions came from, so lint's macOS vet failed), not on load.
Under that load each test took two to three times its slice 1 time, 922 s in all against about 400 quiet, and the wall time was that sum over the width: the machine was the limit, not the pool.

**What landed** (`8c2b968`, r996): in its own `make land`, holding the lock at a load of about 17, the acceptance suite ran 83 tests in **4 min 5 s**, all green but two skipped soaks, against 957 s at the 0.3.0 release and 800 s in slice 1.
That is short of the 1½ minutes estimated from slice 1's quiet table, because a gate's tests now run six at a time on a machine other sessions are working on; the floor is the longest tests (`TestTheStillCityMatchesTheCityDrawnDirectly`, `TestFirstLaunchLoad`, `TestTheCacheSeesTheBinary`, each a minute or more under load), and slice 4's shorter waits and slice 3's selection are what come off it next.
`make test-performance` holds the landing lock too, so nothing lands while it measures.

**`make test-acceptance-locked RUN='^TestName$'`** (`c84a1eb`, r993) takes the landing lock itself and runs only the named tests, through the runner since slice 2, so a worktree session can run acceptance tests without running them beside a landing's gate.
Its test is `TestAcceptanceLocked`, on `make land`'s scratch-repository rig, red with the `flock` taken out.

## Slice 3: landing on what changed

`make land`'s gate is now `lint test-landing`, which runs the unit and integration tests and `make test-acceptance-changed` (`eebf342`, r1002).
The map of the packages each acceptance test runs is kept per revision under `${XDG_CACHE_HOME:-~/.cache}/botropolis/acceptance-map/`, shared by every checkout and worktree, and a landing diffs from the nearest map at an ancestor of `HEAD`.
A change inside `testing/acceptance` selects through the package's own call graph: the tests that reach a changed function, method, constant, variable or type.
It runs everything and saves a new map, saying why, whenever main's last CI run was not green, the map is not an ancestor or is more than 30 commits back, a test was added or removed, a change reaches `TestMain`, or a file cannot be traced.
`ci-status` still never refuses a landing; it decides how much one tests.

Two departures from the agreed tree, both told to the manager: the red-CI rule lives in the tool, so `TestChoose` and `TestTargetedRuns` test it rather than a `land_test.go` probe, and the case for a cost test's package went with slice 2, since the performance tests are no longer in the gate.
The first landing found no map, ran everything under coverage, and saved the map at `eebf342`; landings after it select from that map.

## Answered while building

- **`TestToolchainPins` failing on this machine's Go 1.27.3** (manager, 2026-10-24): filed as [item 227](227-testtoolchainpins-fails-when-the-machines-go-is-not-the-pin.md), and this session fixes it in its own commit citing 227, since it is in this item's landing path; then it closes 227 with `roadmap-close`.
- **How a test names its tier** (manager, 2026-10-24): a marker as each test's first line, `t.Parallel()` for behaviour and a no-op `costTier(t)` for cost, instead of a build tag or name prefix. The fix leaves the mechanism open ("a build tag or name prefix the runner understands"), and this one keeps one `go test` and every test's name. Go runs every non-parallel top-level test first, alone, so the cost tier runs *before* the behaviour tier rather than after; that is still the quiet machine the cost tests need.
- **How many behaviour tests run at once** (manager, 2026-10-24): bounded, not Go's default of `GOMAXPROCS`. Every test starts real binaries and often Xvfb, and fourteen-at-once is what took the load to 178 under item 186. Pick the `-parallel` value by timing two or three against slice 1's table and record it here.
- **Slice 2's test tree** (manager, 2026-10-24): approved as sent, `TestEveryAcceptanceTestNamesItsTier` and `TestTier`, with two additions: the guard itself starts with `t.Parallel()`, and `TestTier` has a case for a test with neither marker, which should be reported as untiered, not defaulted to either tier.
- **Tests that read `pkg/measure`** (manager, 2026-10-24): the cost tier also takes the nine tests that assert work through `pkg/measure`'s process-wide counters (`TestDrive`, `TestAnswerAndComeBack`, `TestFindByThreeWords`, `TestStartASessionAnywhere` and the rest), about 8 s serial, since four failed beside others in the parallel spike (31 s against 403 s). The guard derives the tier rather than listing it: a test starts with `costTier(t)` exactly when it reaches `pkg/measure` or a `/proc` read through the package's own functions, and `t.Parallel()` otherwise.
- **`make land` and a red `main`** (manager, 2026-10-24): the fix's premise that `make land` refuses while `main` is red is wrong; `tools/ci-status` reports and never gates (item 202), as [item 228](228-a-bridge-test-compares-floats-exactly-and-ci-on-macos-is-red.md) records. Slice 3 sends its safety design to the manager before its tests, and making `ci-status` gate would reverse item 202, so that is Aria's.
- **Aria's pause** (Aria, 2026-10-24): she pauses new item launches after item 162's slice 14 to refactor code and tests herself; this item runs to the end first: *"Let it do its refactor first. Then I'll see if there's any more I need"*.
- **[Item 230](230-the-sheet-path-can-still-die-of-an-interrupted-gamepad-open.md)** (manager, 2026-10-24): the sheet path's missing gamepad hold failed a landing; this session carries the fix, as it did 227.
- **Slice 3's safety design** (manager, 2026-10-24): approved as sent, with its test tree. `ci-status` still never refuses a landing (item 202 stands); it now decides only how much `make land` tests: the change-selected run only when the last completed CI run on `main` is green, and the full suite when it is red or unknown. The selection is used only from a shared map at an ancestor of `HEAD` at most 30 commits back, diffed from the map's revision rather than from `github/main`; anything unmappable, a new or removed test, or a change to `TestMain` runs everything; and a change inside `testing/acceptance` selects through the guard's call graph. The 30 is the manager's choice, to be retuned against this item's timing once it has run a week.
- **The CPU and memory tests leave the landing gate** (Aria, 2026-10-24, in this session's window: *"Perhaps we should split the performance tests into their own group that can be run separately on demand when we are ready for it"*, then *"Perf manager + release"* for where they run): they leave `make land` and `make test` for `make test-performance`, which the performance manager runs on demand and before each release, and the release workflow runs, as it runs `make bench`. So the tiers are three: `performanceTier(t)` (skipped unless `BOTROPOLIS_PERFORMANCE=1`, for tests reaching CPU or memory measurement or `/proc`), `workTier(t)` (serial in the gate, for the nine tests reading `pkg/measure`'s work counters), and `t.Parallel()`; the guard still derives each. `docs/roles.md` and the performance manager's agent file now name the duty.
- **What runs the performance tests between releases** (Aria, 2026-10-24, *"Start the perf manager after your refactor"*): when her refactor pause lifts, the roadmap manager starts the performance manager, which runs `make test-performance` after each landing that touches drawing, memory or the daemon.
- **Parallel by process, not by goroutine** (manager, 2026-10-24): `t.Parallel()` inside one binary collides, since `RunIsolated` gives the whole process one home (shared daemon and city sockets, caches, checkpoints; `t.Setenv` panics under it). So `make test-acceptance` runs `tools/acceptance-targets run`, which builds the test binary once and runs each test in its own process from a pool of `ACCEPTANCE_PARALLEL`, each with its own isolated home. `workTier` goes, since `pkg/measure`'s counters are per process; `performanceTier(t)` stays, derived by the guard both ways. `TestFirstLaunch` and `TestFirstLaunchLoad` split into behaviour tests and `…Cost` tests, so first launch stays covered on every landing. The runner lists tests with `-test.list`, so none can be left out; reports every failure by name; exits non-zero on any; and has a test tree of its own approved before it is written.
- **The runner's test tree** (manager, 2026-10-24): approved as sent, `TestRunnable`, `TestReport`, `TestRunPool` and `TestDefaultParallel` in `tools/acceptance-targets/targets`, with one addition: an end-to-end test that builds a small fixture package (one passing test, one failing, one that panics) with the real `go test -c` and runs it through `run`, which must exit non-zero naming both, so the wiring of flags and binaries is tested as well as the pool.
- **`TestFirstLaunch` under load** (manager, 2026-10-24): its `untilIdle` gives up on the wall clock, so it can flake in the parallel behaviour tier; slice 4 fixes it first, by waiting on the event, and until then a flake makes it serial, never a longer timeout. The pool's default stays 6 wide: the one failure seen at 6 was a missing `//go:build linux`, not load.
- **Running one acceptance test under the lock** (manager, 2026-10-24): a worktree session's guard refuses `flock /tmp/botropolis-land.lock go test …`, since it cannot see what flock runs, while `make land` gets through because its flock is inside make (item 222 found it). So this item adds a target, such as `make test-acceptance-locked RUN='^TestName$'`, that takes the landing lock itself and runs only those acceptance tests, unpiped, with their exit code; it lands early and on its own, tested as `make land`'s lock is.
- **`make test-acceptance-locked`'s tree** (manager, 2026-10-24): approved as sent, `TestAcceptanceLocked` on `land_test.go`'s scratch-repo rig with a `LOCKED_GATE` probe: it waits for the lock and says so, passes `RUN` unchanged, exits non-zero on failure, refuses without `RUN`, and pipes nothing. Until it lands, no session wraps a command in a bash script to get it past the worktree guard: that guard is what keeps a worktree session's git in its worktree, and a script hides what it runs.
