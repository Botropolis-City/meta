# 160. The usage probe starts every MCP server the user has configured, every refresh

**Fixed 2026-10-21 (`c15d983`, r874). Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the background-helper budget Aria set the same day.**

Depends on: nothing

Landed: slice 1 (`ac51be9`, r872).
Landed: slice 2 (`c15d983`, r874).

`RefreshUtilization` (`pkg/claude/usage.go:262`) runs `claude -p /usage` with no other flags, from the city's gauges (`pkg/render/gauges.go:406`) every `usage_refresh` interval when one is set.
`Summarise` (`pkg/claude/summary.go:160`) already passes `--setting-sources ""`, `--strict-mcp-config` and `--tools ""` for exactly this reason, and its comment says why: without them every connected MCP server comes along.
The probe passes none of them, so every refresh starts Claude Code with the user's settings, hooks, plugins and MCP servers.

**What it costs**: on the laptop, with `usage_refresh = '5m'`, the city ran the probe three times in fifteen minutes, and each time its process tree held seven processes — Claude Code and four MCP servers launched through npm, with their helpers — peaking at **806 MiB of `Private_Dirty`** ([the laptop report](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md), finding 7).
On the Core Ultra 7 265U, the same command run by hand from the probe's directory, sampled with `perf-sample --tree` ([the 265U report](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md)):

| how it was run | peak `Private_Dirty`, whole tree | processes | answered |
| --- | --- | --- | --- |
| `claude -p /usage`, as `RefreshUtilization` runs it | 904–970 MiB | 5 | yes |
| `claude -p /usage --setting-sources "" --strict-mcp-config` | 408–426 MiB | 1 | yes |

**So the isolation flags halve it and are not enough**: Claude Code on its own is over the 300 MiB budget.
And `--tools ""` cannot simply be copied from `Summarise`: it takes several values, so after it `/usage` is read as a tool name and the run fails with "Input must be provided"; `Summarise` gets away with it because its prompt arrives on stdin.

RefreshUtilization's own comment says it "belongs behind an explicit user action and nowhere else"; `usage_refresh` made it periodic (item 79), and the comment was not updated.

**The budget** ([budgets.md](../performance/budgets.md), *Background helpers*): ≤ 300 MiB peak across the helper's whole process tree; runs for at most 10% of its interval (≤ 30 s of a 5-minute refresh); built from deltas and cached data rather than from scratch; never starts the user's MCP servers; never more than one helper at a time.
Aria, 2026-10-19: "if it were to take 2 minutes to update every 5 minutes, that feels bad. We should try to make this quicker and less memory using deltas and cached data."

## The fix

1. Pass `--setting-sources ""` and `--strict-mcp-config`, with `/usage` before them; both were checked on the 265U to keep the login and return the figures.
2. That leaves Claude Code alone at ~420 MiB, so find the leaner way to get the figures: read what Claude Code caches between refreshes, refresh only when it is stale, and spawn nothing when the cached figures are fresh enough. Measure the tree's peak and wall time per refresh with `perf-sample --tree` against the budget.
3. Fix the comment on `RefreshUtilization`, and hold the one-helper-at-a-time rule across the probe and summaries, not just within each.

Tests: a fake `claude` on `PATH` that records its arguments, asserting the probe passes `--strict-mcp-config` and an empty `--setting-sources`; a test that a refresh never starts while a summary runs, or the reverse.

**Aria, 2026-10-21, on getting the probe under budget:** *"Probe less often."* Botropolis keeps using `claude -p /usage` (isolated, with no settings and no MCP servers), runs it only while the city is open and less often, and accepts the ~420 MiB that Claude Code itself needs while a probe runs. It does not read `~/.claude/.credentials.json` or call the usage endpoint directly, which was offered and declined.

## Measured, 2026-10-21

Six runs of the isolated probe, `claude -p /usage --setting-sources "" --strict-mcp-config`, from the probe's directory on the 14-core desktop, each sampled with `perf-sample --tree --interval 0.25`, while other sessions held the load average at 15–22:

| measure | per probe |
| --- | --- |
| peak `Private_Dirty`, whole tree | 187–224 MiB (the 265U: 408–426 MiB) |
| processes | 2–4: `claude`, and the `sh` and `git` it starts |
| wall time | 25–45 s, at about 220% CPU |

The wall time is not the "about four seconds" the code assumed: `/usage` now also prints insights such as its top skills and which sessions to stop, which it gets by reading the transcripts.
The slowest run took 44.8 s, against a 45 s timeout.

Per hour, at 45 s a probe:

| `usage_refresh` | probes | probing | duty cycle |
| --- | --- | --- | --- |
| 5m | 12 | 9 min | 15%, over budget |
| 15m | 4 | 3 min | 5% |
| 30m | 2 | 1.5 min | 2.5% |
| 1h | 1 | 45 s | 1.25% |

So slice 2 sets a floor of 15 minutes, raises anything lower to it, probes on the schedule only while someone can see the window, and gives the probe 90 s.

**The upstream gap**: Claude Code alone, with no settings and no MCP servers, needs 200–420 MiB and up to 45 s to answer `/usage`, which is Claude Code's own floor and over the 300 MiB budget on the 265U.
Botropolis cannot get under it while it asks Claude Code, and Aria chose to keep asking it; what would close the gap is a cheaper way in Claude Code itself to refresh the cached figures.

## Closed

Slice 1 (`ac51be9`, r872) runs the probe with an empty `--setting-sources` and `--strict-mcp-config`, so it no longer loads the person's settings, hooks and plugins or starts their MCP servers, and fixes the comment on `RefreshUtilization`.
It also gives the probe and summaries one helper slot between them: each waits for it until its own context ends, so two summaries now run one after the other too.
`pkg/claude/helper_test.go` holds both, with a fake `claude` that records its arguments and one that holds the slot.

Slice 2 (`c15d983`, r874) follows Aria's ruling: `usage_refresh` under 15 minutes now means 15 minutes rather than being refused, so old configs still read, and the settings menu drops 5m.
The schedule probes only while someone can see the window, the `u` key still asks whenever pressed, and the probe's timeout is now 90 s.
`TestUsageProbesOverAnHour` in `pkg/render/usageschedule_test.go` steps the schedule through an hour at 1m, 5m, 15m and 1h and holds the probing to a tenth of it, at the measured 45 s a probe; an unwatched hour starts none.
Both slices have changelog entries.

**For Aria**: what the item asked for in step 2, reading Claude Code's cache and spawning nothing when it is fresh, was already the schedule's behaviour, since it measures from the cache's own `fetchedAtMs`; nothing new was needed there.
The memory per probe stays at Claude Code's own floor, recorded above as the upstream gap, so the budget is now met on time spent probing and on isolation, and on memory only on machines where Claude Code alone stays under 300 MiB.
The boats' card already shows each reading's age ("read 12m ago (u to refresh)"), so a reading up to 15 minutes old says so.
