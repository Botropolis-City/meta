# 226. The acceptance suite takes sixteen minutes on every landing

**Open, in progress since 2026-10-24 in the session "item 226". Filed 2026-10-24 (r968) at Aria's request, and prioritised by her: start it before other ready items. Nobody's call — the shape is agreed below.**

Depends on: nothing
Landed: slice 1 (`0922f2b`, r969).

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
