# 200. On macOS the first-launch ingest runs at normal priority, unmeasured

**Open, in progress since 2026-10-22 in the session "item 200". Filed 2026-10-22 (r882) at Aria's request, from item 159's macOS deviation. Nobody's call — the budget is set; this item measures and meets it on macOS.**

Depends on: 159 (slice 1)

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

## Sources

XNU and libpthread source (github.com/apple-oss-distributions); the `setiopolicy_np(3)` and `launchd.plist(5)` man pages; Apple's Energy Efficiency Guide; eclecticlight.co on QoS and core types; golang/go#82146; GitHub's runner documentation.
