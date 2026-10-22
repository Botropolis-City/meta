# 200. On macOS the first-launch ingest runs at normal priority, unmeasured

**Done 2026-10-22 (`103222d`, r900). Filed 2026-10-22 (r882) at Aria's request, from item 159's macOS deviation. Nobody's call — the budget is set; this item measures and meets it on macOS.**

Depends on: 159 (slice 1)
Landed: slice 1 (`7118d4f`, r891).
Landed: slice 2 (`103222d`, r900).

[Item 159](159-first-launch-takes-the-machine.md) put the first-launch ingest at nice 10 on Linux, after measuring that it doesn't bring back [item 138](138-state-changes-lag-while-statistics-backfill.md)'s inversion (Go's stop-the-world waiting on a low-priority thread). On macOS it ships with the pacer alone (≤ half a core), because the only no-cgo call, `setpriority(PRIO_DARWIN_THREAD, 0, PRIO_DARWIN_BG)`, throttles hard and nobody has a Mac to measure it on. So "at background priority" is unmet on macOS.

## What is known (item 159's research)

- **`PRIO_DARWIN_BG`** is macOS's analogue of nice 19 plus idle I/O. It clamps the thread to priority 4 (default 31) and to QoS background, with I/O tier 2 and timer coalescing, and strips the thread's QoS. On Apple silicon, QoS background runs on efficiency cores only (observed, not documented). `x/sys` exposes it; `PRIO_DARWIN_THREAD = 3`, `PRIO_DARWIN_BG = 0x1000`.
- **QoS `UTILITY`** (priority 20, I/O tier 1) is the closer analogue of the nice 10 shipped on Linux. It is set with `pthread_set_qos_class_self_np`, which is libSystem-only and reachable without cgo through purego (already in `go.mod`) or a hand-written trampoline.
- **I/O alone**: `setiopolicy_np(IOPOL_TYPE_DISK, IOPOL_SCOPE_THREAD, IOPOL_THROTTLE)`, through `iopolicysys` (syscall 322, `IOPOL_CMD_SET = 2`) or a trampoline. Its throttling sleeps inside the syscall, where the stop-the-world doesn't wait on the thread, so it should be free of the inversion. A thread I/O policy strips QoS, so `UTILITY` and a thread I/O policy can't be combined; `PRIO_DARWIN_BG` plus `IOPOL_THROTTLE` can.
- **The inversion on macOS**: the stop-the-world waits for each thread to be scheduled and take a signal. No lock with an owner is involved, so macOS's priority-inversion avoidance (turnstiles, QoS overrides) can't help. The bound is the scheduler's latency: about 250 ms at worst for background, 150 ms for utility. Two pauses per GC cycle at background on a busy machine is close to item 138's 600 ms bound. golang/go#82146 (signal-resend storms on slow cores, fixed by `GODEBUG=asyncpreemptoff=1`) has the same shape.
- **launchd**: the plist comes from the Homebrew formula's service block, which supports `process_type` and `nice` but not `LowPriorityIO`. A whole-process `Background` would starve the daemon's serving, so it is rejected; a whole-process nice is mild but stops singling out the ingest.
- **An alternative design**: run the ingest in a child process at background priority, so its GC never couples to the daemon's, on both OSes.

## The test

Item 138's inversion test ported to darwin (behind a build tag, run by CI's macOS jobs), loaded with 2 × `hw.logicalcpu` busy **child processes** (not goroutines, which the stop-the-world stops too). Matrix: {none, `PRIO_DARWIN_BG`, QoS utility, QoS background, `IOPOL_THROTTLE` only, `PRIO_DARWIN_BG` + `IOPOL_THROTTLE`} × {default, `asyncpreemptoff=1`}.
Measure the state-change bound (item 138's 600 ms), `runtime/metrics` `/sched/pauses/stopping/gc:seconds` (max and p99 — the inversion itself), and the largest gap in a 10 ms heartbeat. Assert that the ingest made progress, and that each policy really took effect.
Expected winner (inferred, not measured): QoS utility alone, or `IOPOL_THROTTLE` alone if CPU priority isn't needed. Ship the winner, gated by the ported test.

**CI caveat**: `macos-26` (a 3-vCPU M1 VM) and `macos-26-intel` run as VMs whose threads land on the host's performance cores, so CI can't show confinement to efficiency cores. The background variants need one run on a real Apple-silicon Mac before they ship; record that run in this item.

## What landed

- **Slice 1, measure** (`7118d4f`, r891; fixed at `a7aa93d`, r895): `pkg/state/priority_darwin.go` can put the pass's thread under any of the six policies, through x/sys for `PRIO_DARWIN_BG` and purego into libSystem for QoS and the I/O policy, and reads each back: `PRIO_DARWIN_BG` from `getpriority`, the QoS class, the disk I/O policy, and the thread's base priority from `thread_info`.
  `pkg/daemon/backfill_darwin_test.go` is item 138's test ported, and runs in a step of its own in CI's `test-macos` jobs.
  The first run took both macOS jobs down, which is the first finding below, so a cell with no result in 90 s is now recorded as frozen, and the matrix no longer runs beside the other packages' tests: there, its busy loops held the state package's `PRIO_DARWIN_BG` test thread off the CPU for 30 minutes.
- **Slice 2, ship** (`103222d`, r900): the pass's thread gets `IOPOL_THROTTLE` and keeps its CPU priority, the macOS counterpart of the idle I/O class it gets on Linux.
  The CI step now gates the shipped policy beside 2 × `hw.logicalcpu` busy processes: the I/O policy applied, the pass outside `PRIO_DARWIN_BG`, the ingest moving, and a state change within the debounce plus 500 ms.
  `BOTROPOLIS_DARWIN_PRIORITY_MATRIX=all` still measures every policy.
  At r900 the gate passed on both runners (run 39777293237): a state change in 104 ms on Apple silicon and 109 ms on Intel, with 988 and 308 yields.
  It was red before the switch in the sense that every "none" cell above read the pass's disk I/O policy as 0; with no Mac here, it could not be run red locally.
- **Changelog:** a line under *Fixed*, beside item 159's entry.

## Measured

Three CI runs of each job on 2026-10-22, at `a7aa93d` (run 39766878344, attempts 1-4): `macos-26` (Apple silicon, 3 cores, 6 busy processes) and `macos-26-intel` (4 cores, 8 busy processes).
Each cell is *state change ms / largest stopping pause ms / largest heartbeat gap ms / ingest yields* in the 2-3 s window, one per run; FROZE is no result within 90 s.
Stopping pauses are the upper bound of their histogram bucket, so 4295.0 means at least 2.1 s.

| runner | policy | GODEBUG | run 1 | run 2 | run 3 |
| --- | --- | --- | --- | --- | --- |
| Apple silicon | none | default | 104/0.8/10/589 | 101/0.7/10/948 | 106/0.5/20/602 |
| Apple silicon | none | asyncpreemptoff | 103/2.6/10/751 | 103/1.0/10/1086 | 101/1.3/10/589 |
| Apple silicon | darwin-bg | default | FROZE | FROZE | FROZE |
| Apple silicon | darwin-bg | asyncpreemptoff | FROZE | FROZE | FROZE |
| Apple silicon | qos-utility | default | 105/0.3/10/854 | 101/1.3/19/710 | 111/0.8/10/620 |
| Apple silicon | qos-utility | asyncpreemptoff | 104/1.0/10/891 | 102/0.9/10/728 | 101/0.7/10/724 |
| Apple silicon | qos-background | default | FROZE | FROZE | FROZE |
| Apple silicon | qos-background | asyncpreemptoff | FROZE | FROZE | FROZE |
| Apple silicon | io-throttle | default | 105/1.0/10/703 | 101/0.7/10/735 | 103/2.6/10/790 |
| Apple silicon | io-throttle | asyncpreemptoff | 105/1.0/10/755 | 101/0.7/10/993 | 106/0.9/10/848 |
| Apple silicon | darwin-bg+io-throttle | default | FROZE | FROZE | 105/0.0/10/1 |
| Apple silicon | darwin-bg+io-throttle | asyncpreemptoff | FROZE | FROZE | 106/0.0/10/6 |
| Intel | none | default | 108/1.6/40/260 | 103/1.3/130/152 | 202/100.7/110/234 |
| Intel | none | asyncpreemptoff | 132/21.0/40/248 | 118/3.1/139/144 | 121/1.6/30/194 |
| Intel | darwin-bg | default | 126/1.0/30/140 | 107/12.6/110/54 | 106/16.8/70/66 |
| Intel | darwin-bg | asyncpreemptoff | 287/0.3/219/165 | 105/16.8/269/38 | 115/234.9/29/76 |
| Intel | qos-utility | default | 103/83.9/80/217 | 110/2.6/30/114 | 122/1.8/30/206 |
| Intel | qos-utility | asyncpreemptoff | 110/1.8/40/256 | 105/3.7/130/98 | 115/0.7/129/169 |
| Intel | qos-background | default | 105/10.5/30/105 | 114/6.3/30/50 | 105/3.1/40/74 |
| Intel | qos-background | asyncpreemptoff | 107/6.3/150/121 | 110/1.6/110/25 | 130/8.4/70/130 |
| Intel | io-throttle | default | 101/0.5/30/265 | 105/3.7/29/152 | 105/1.0/160/195 |
| Intel | io-throttle | asyncpreemptoff | 114/3.1/30/228 | 103/1.6/29/135 | 102/1.6/40/221 |
| Intel | darwin-bg+io-throttle | default | 103/2.6/99/95 | 109/1.0/29/39 | 105/2.6/39/131 |
| Intel | darwin-bg+io-throttle | asyncpreemptoff | 108/4295.0/39/37 | 104/0.8/30/47 | 103/0.8/30/108 |

What it says:

- **On Apple silicon the background band does not slow the daemon, it stops it.**
  A thread at priority 4 on three busy cores never ran, and the collector's stop-the-world waited for it, so the whole process froze: item 138's inversion with no bound at all, and `asyncpreemptoff=1` did not help.
  On the first run, before the deadline, one such child sat for over nine minutes.
  The research's estimate of about 250 ms of scheduler latency at worst did not hold on a VM with no efficiency cores, and nothing here shows it holds on a real Mac.
- **On Intel the background band ran, at a cost**: fewer yields than none, and the only stopping pauses of hundreds of milliseconds or more, 235 ms and at least 2.1 s.
- **QoS utility cannot be told from none on a CI runner.** Every thread the test read was already at base priority 20, utility's, before any policy was applied (the runners start jobs below the default 31), so applying utility changed nothing measurable.
  By the manager's ruling (2026-10-22), an unmeasured utility does not ship.
- **`IOPOL_THROTTLE` took effect every time and measured the same as none** on both runners, as the research expected: its throttling sleeps inside a system call, where the stop-the-world does not wait on the thread.
- **Two corrections to the research above:** `x/sys` does not expose `PRIO_DARWIN_THREAD` or `PRIO_DARWIN_BG`, so they are defined in `priority_darwin.go` (3 and `0x1000`); and a thread I/O policy strips the thread's QoS class, as said, which also holds for `PRIO_DARWIN_BG`: both read back as unspecified.

## Not shipped, and why

- **The background variants** (`PRIO_DARWIN_BG`, QoS background, and either with `IOPOL_THROTTLE`): they froze the daemon on CI's Apple-silicon runner.
  The CI caveat above asked for a run on a real Apple-silicon Mac before they ship; nobody has one, and after these results they would need more than one run to clear.
  The matrix is ready for it: `BOTROPOLIS_DARWIN_PRIORITY_MATRIX=all go test -count=1 -v -run '^TestStateChangeDuringBackfillOnDarwin$' ./pkg/daemon/`.
- **QoS utility**: no CI runner can show it doing anything, so it would ship unmeasured.
  A Mac whose jobs start at the default priority, 31, could measure it with the same command.
- So on macOS "at background priority" is met for I/O and not for CPU, where the pacer alone keeps the pass to half a core, as item 159 shipped it.
  The alternative design above, the ingest in a child process whose collector never couples to the daemon's, is the way to lower its CPU priority without this risk, on both systems; it is not filed.

## Closed

Done at `103222d` (r900): on macOS the first-launch ingest's disk reads are throttled, gated in CI on both macOS runners by item 138's inversion test.
**For Aria, one deviation:** the budget's "at background priority" is met on macOS for I/O and not for CPU, because every lower CPU priority that CI could measure froze or stalled the daemon, and the one that might not (QoS utility) cannot be measured on CI.
The pacer still keeps the pass to half a core there.
Lowering its CPU priority safely would take the ingest into a child process, as the alternative design above says; that is not filed.

## Sources

XNU and libpthread source (github.com/apple-oss-distributions); the `setiopolicy_np(3)` and `launchd.plist(5)` man pages; Apple's Energy Efficiency Guide; eclecticlight.co on QoS and core types; golang/go#82146; GitHub's runner documentation.
