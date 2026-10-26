# 270. The city freezes with hundreds of districts and groups of hundreds

**Open, in progress since 2026-10-26 in the session "item 270". Filed 2026-10-26 (r1099), from Aria's start of 0.3.1 on another laptop with a long history. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`284256c`, r1102).
Landed: slice 2 (`f3fc805`, r1107).
Landed: slice 3 (`3d39de9`, r1108).
Landed: slice 5 (`6c3ea21`, r1109).
Landed: slice 6 (`5aaca19`, r1118).

Aria, 2026-10-26: *"We have way too many districts/groups/sessions. Every single tmp directory and probably work tree dir and such got its own district with one session and groups were generated for all of it. The UI is frozen and unusable, but at least the CPU and memory didn't spike to 100."*
Minutes later the city would not exit either.

What that laptop holds, measured read-only over ssh: 1,558 catalogued sessions in 559 distinct directories, so 559 districts; 48 groups, the largest with 781, 182, 91, 86, 72, 65 and 61 members.
The frozen city sat at about 2 GiB resident, sleeping, with 28 threads and under 10% of a core; the daemon was well.
The performance suite's largest city is 200 sessions in 150 projects, and `TestDaemonWithTwoThousandSessions` puts its sessions in a few directories, so nothing has ever drawn hundreds of districts.

Items 271 to 274 take most of those districts and groups off that map; this item makes the city survive them anyway, since a large real history is a fact of some machines.

## Where it costs (from a read of the code at r1099; to be confirmed by a profile)

- Per frame, unculled: each district's monument, sign and plate check (`pkg/render/iso.go`, around 782–868) and the top-down loops (`pkg/render/game.go`, around 1028).
- Group lines are drawn twice a frame, unculled, every stroke and station with a hit box (`pkg/render/iso.go` around 880; `pkg/render/lines.go` `groupLines`).
- Label layout is O(n²) per frame (`pkg/render/labellayout.go` `layoutLabels`), fed a plate per district plus station labels.
- Per snapshot: `placeLines` (groups × buildings) with `coordinator` rebuilding a district map per group (`pkg/city/lines.go`), and `plan.assign` rebuilding ring slots per new district (`pkg/plan/plan.go`), about O(n²).
- A freeze at low CPU also fits the main loop blocked rather than busy, so the first step is a goroutine dump of a frozen city (`SIGQUIT`) and a CPU profile, not a guess.

## The fix

1. A staged city at that laptop's scale — 600 districts, 1,600 sessions, groups of 800 — built from `botropolis-demo synth-home` (item 248), never from a real history, as a performance-tier case; first make it reproduce the freeze.
2. Profile it, fix what dominates, cull what is off screen (signs, monuments, plates, lines) and make the label layout sub-quadratic.
3. Gate it: the city at that scale opens, pans and quits, within the performance budgets, and the case stays in the suite.
4. Quitting must always work: `q` then `y` exits even when a frame or a snapshot is slow.

## Answered while building

- **Slice 4's measurement at the stress scale** (session, 2026-10-26; synthetic, 2,400 sessions in 900 districts, a group of 800, real city under Xvfb on its own daemon, a busy machine): first frame 13.5 s against a map within 5 s; Private_Dirty peak 936 MiB, within 1 GiB; settled 693 MiB against 512; drawing 34–55 ms a frame (40 quiet) against 10 ms of CPU. Without a daemon, 1.3 GiB peak and 940 MiB settled, because group detection runs in the city. About 36% of the fitted frame is item 212's noting and dry pass and 20% the depth sort.
- **Whether the case lands red** (manager, 2026-10-26): neither red nor loosened; slice 4 stays unlanded until Aria sets the bars at this scale, since a red performance-tier case would fail 0.3.2's pre-release run over a scale the release does not claim, and reporting instead of gating would loosen a limit without her. Meanwhile the session looks at the first frame (whether the first-launch progressive map fails at this size, which would be a defect) and at the ~490 MB outside the Go heap.
