# 0.2.2 against 0.1.7 on an integrated-graphics laptop, 2026-10-19

**Rig:** Intel Core Ultra 7 255H, 16 threads, 31 GiB, 15 GiB swap; the desktop draws on the **integrated Intel Arc GPU** (i915), with a discrete NVIDIA card idle beside it; 1920×1200, i3 on X11, Arch Linux, kernel 7.2.
This is a strong machine, and **not** the reference: see [the README](../README.md).
Every finding below is worse on a modest one, because none of the large numbers depends on the machine's size.
**Builds:** 0.2.2 (r745) as packaged; 0.1.7 (r409) and 0.2.2 built from `git archive` of their tags with go 1.27.2.
**History on disk:** 1,031 transcripts, 1.2 GiB, 71 projects, 14 written in the last hour, about 30 `claude` processes running.
**Runs:** all five in [method.md](../method.md), between 16:13 and 16:50 MDT; the raw runs stayed on the machine.

## What happened

Aria upgraded 0.1.7 to 0.2.2 at 12:07, and the 0.1.7 daemon kept running until it was restarted at 16:00.
systemd's accounting for that daemon: **7 min 31 s of CPU over 32 h 48 min, about 0.4% of a core, with a 105.6 MB memory peak.**
The 0.2.2 daemon that replaced it used 180 s of CPU in its first nine minutes.
And with the city open, the machine ran out of memory: 8.8 GiB of it was in swap when this analysis started, with the city already closed.

## Findings

Most expensive first.

1. **The city's Go heap holds 2.4–3.7 GB after start-up in 0.2.2, against 161 MB in 0.1.7**, and the start-up burst reaches 5–8 GB within four seconds (run 3, gctrace).
   Live heap after successive collections went 2.1 → 4.1 → 7.7 GB in the first 7 s, and the forced collection after the atlas upload left 3.7 GB live, which stayed for the rest of the 15-minute run.
   The same happens whether or not the window is focused: a second run that drew 360 frames reached 5.0 GB live at 3.6 s and settled at 2.4 GB.
   A heap profile of 0.2.2 (`perf-pprof-build`, under Xvfb, where the burst is smaller but the same shape) puts **~80% of the heap in Ebitengine's draw-command queue**: `graphicscommand.(*commandQueue).EnqueueDrawTrianglesCommand`, reached from `render.(*Game).Draw` → `drawIso` through `drawSprite`/`kitLifted` (49%), `queueDistrictPlate` → `plate` → `text` (28%), `isoTree`/`agedLots` (24%) and `composeStatic` (9%).
   The queue reuses its buffers across frames, so if the first frames enqueue a vast number of triangles, the capacity they grew to is kept.
   **What makes the first frames enqueue so much is not established here**; candidates in the window r409..r745 are listed under *For whoever fixes it*.
2. **The city's GPU memory on integrated graphics is 1.9–3.0 GB in 0.2.2, against 0.9 GB in 0.1.7** (`drm-total-system0` from the i915 fdinfo).
   On integrated graphics that is system RAM, and it appears in no RSS figure.
   0.1.7's 0.9 GB is itself far over any budget for a modest laptop.
3. **The daemon spends ~61% of its CPU in the garbage collector, because its heap is capped at 16 MiB** (`appd.DefaultMemoryLimit`).
   Its live heap sits close to the cap, so it collects continuously: **1,474 collections a minute**, against 19 for 0.1.7.
   Run side by side for the same five minutes, `GOMEMLIMIT=256MiB` took 0.2.2 from 6.3% to **0.6%** of a core mean, and p95 from 45% to 4.5%, at a cost of 0.8 MiB of `Private_Dirty`.
   A cold start showed the same: 26.5 CPU-seconds and 7,252 collections, against 3.9 and 188.
4. **Of the daemon's real work, 77% is group detection**, `group.Detect` → `detection.pair` → `Wording.Related`/`Shared`: a comparison of every pair of sessions (60 s CPU profile).
   `applyGroups` re-runs it whenever `history.jsonl` changes, and `history.jsonl` changes on every prompt in every session.
5. **The production daemon averaged 35.6% of a core over ten minutes with no city open** (p95 166%, peak 284%, 95 seconds at or above one full core).
   Its `Private_Dirty` was flat at 17.5 MiB, so the daemon's problem is CPU, not memory.
   The A/B copies, which receive no hook pushes, ran at 6–15%; the difference is hook-driven rebuilds and the rescan → ingest → rescan loop that a changed heft triggers.
   On Linux, each attachment probe also reads all of `/proc/net/unix` (127 KB, 1,782 sockets here) once per socket probed.
6. **First launch on 0.2.2 reads ~1 GB of history in about eight seconds at up to four cores** (cold start, empty state directory), against 70 MiB and no core for 0.1.7.
   Here that is eight seconds.
   On a four-core laptop with a slower disk it is the whole machine for much longer, and it grows with the history.
7. **The usage probe starts every MCP server the user has configured, every refresh.**
   With `usage_refresh = '5m'`, the city ran `claude -p /usage` three times in fifteen minutes, and each time its process tree held seven processes (Claude Code and four MCP servers launched through npm, with their helpers), peaking at **806 MiB of `Private_Dirty`** for a few seconds.
   `RefreshUtilization` passes none of the flags `Summarise` already passes for exactly this reason (`--strict-mcp-config`, `--setting-sources ""`, `--tools ""`).
8. **Drawing a frame costs twice the CPU**: 41 ms/frame in 0.2.2 against 21.6 ms in 0.1.7 (`BOTROPOLIS_FRAMETIME`), over the 33 ms a 30-tick frame has.

## Daemon

| build | run | CPU mean | CPU p95 | GCs/min | Private_Dirty | read MiB/s mean | sample |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.1.7, before the upgrade | systemd | 0.4% | — | — | 105.6 MB peak (cgroup) | — | 32 h 48 min |
| 0.2.2, production | at rest | 35.6% | 166% | — | 17.5 MiB | — | 593 s at 1 s |
| 0.1.7 | A/B 1 | 0.7% | 3.5% | — | 8.0 MiB | 1.1 | 300 s at 2 s |
| 0.2.2 | A/B 1 | 14.9% | 64% | — | 17.1 MiB | 2.6 | same window |
| 0.1.7 | A/B 2 | 0.2% | 2.0% | 19 | 8.3 MiB | 0.3 | 300 s at 2 s |
| 0.2.2 | A/B 2 | 6.3% | 45% | 1,474 | 17.8 MiB | 0.7 | same window |
| 0.2.2, `GOMEMLIMIT=256MiB` | A/B 2 | 0.6% | 4.5% | 45 | 18.6 MiB | 0.7 | same window |

## First launch

| build | seconds at ≥50% CPU | peak CPU | CPU-seconds | collections | read | Private_Dirty peak |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1.7 | 0 | 19% | 0.3 | 30 | 70 MiB | 8.1 MiB |
| 0.2.2 | ~8 | 391% | 26.5 | 7,252 | 954 MiB | 17.3 MiB |
| 0.2.2, `GOMEMLIMIT=256MiB` | ~4 | 111% | 3.9 | 188 | 960 MiB | 26.7 MiB |

## City

The real display, integrated GPU, the window opened as i3 places it.

| build | state | frames drawn | ms/frame | CPU mean | Private_Dirty settled | Private_Dirty peak | GPU MiB | Go live heap | sample |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.1.7 | focused, then not | 600 | 21.6 | 12.0% | 212 MiB | 1,240 MiB | 939 | 161 MB | 240 s |
| 0.2.2 | never focused | 0 | — | 1.7% | 3,978 MiB | 8,203 MiB | 3,002 | 3,714 MB | 900 s, hidden at 600 |
| 0.2.2 | focused, then not | 360 | 41.2 | — | 2,545 MiB | 6,943 MiB | 1,920 | 2,444 MB | 150 s |

Under Xvfb, which uses llvmpipe and is useful only to compare builds: 0.1.7 settled at 86–98 MB of live heap and 0.2.2 climbed to 475 MB within 3.3 s.

## For whoever fixes it

- **City heap:** take `perf-pprof-build v0.2.2` and a heap profile on the real display during the first four seconds, then bisect r409..r745 with `perf-city` on the Go live heap.
  0.2.2's own change list for the first frames includes the atlas uploaded a page per update (item 70, `1af9c33`), the district plates and map labels (`5b304e9`, item 102), the car-fade and plan layers (items 108 and 106), and the shore texture sized to the island (item 85 slice 3).
  All eight kit pages of both zoom levels stay on the GPU whatever the zoom (`render/kits.go`), which is 128 MiB of the GPU figure before anything else.
- **Daemon GC:** raise or remove `DefaultMemoryLimit`, and stop calling `debug.FreeOSMemory()` after every rescan; measure with `perf-daemon-ab` against 0.1.7.
- **Group detection:** do not re-run the pairwise detection on every `history.jsonl` change; key it on what the detection actually reads, or make it incremental.
- **First launch:** the ingest should run at one core or less, at background priority, resumable, with a percentage the city can show — see [budgets.md](../budgets.md).
- **Usage probe:** pass the same isolation flags `Summarise` passes.

## What it does not show

- **What enqueues the first frames' triangles** is attributed to call sites, not explained.
- **macOS was not measured.** Its integrated graphics share RAM the same way, but its drivers and allocators differ, and `perf-sample` reads `/proc`, which macOS does not have.
  A macOS port of the sampler (`ps`, `vmmap`, `footprint`) is the next tool to write.
- **Focus could not be controlled** without moving Aria's pointer, so each city run took the focus it got; the frame counts say which state each row is.
- **The machine was not quiet:** about 30 Claude Code sessions were working, which is why each comparison was run side by side and why absolute daemon figures vary between windows (6.3% and 14.9% for the same build).
- **Nothing was measured for longer than 15 minutes**, so a slow leak after the start-up burst would not show; the slopes over the settled part of each run were within ±5 MiB/min.

## Reproduce

From the meta repository's root, with botropolis checked out beside it:

```sh
performance/tools/perf-env
make perf-daemon PERF_SECONDS=600
for t in v0.1.7 v0.2.2; do performance/tools/perf-pprof-build $t /tmp/perf-$t; done
printf '#!/bin/sh\nGOMEMLIMIT=256MiB exec /tmp/perf-v0.2.2/botropolisd "$@"\n' >/tmp/perf-memlimit && chmod +x /tmp/perf-memlimit
performance/tools/perf-daemon-ab --seconds 300 v0.1.7=/tmp/perf-v0.1.7/botropolisd v0.2.2=/tmp/perf-v0.2.2/botropolisd memlimit=/tmp/perf-memlimit
performance/tools/perf-daemon-ab --cold --seconds 900 --interval 1 v0.1.7=/tmp/perf-v0.1.7/botropolisd v0.2.2=/tmp/perf-v0.2.2/botropolisd memlimit=/tmp/perf-memlimit
performance/tools/perf-city --seconds 900 --hide-after 600
performance/tools/perf-city --bin /tmp/perf-v0.1.7/botropolis --seconds 240
```
