# 160. The usage probe starts every MCP server the user has configured, every refresh

**Open, in progress since 2026-10-21 in the session "item 160". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the background-helper budget Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing

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
