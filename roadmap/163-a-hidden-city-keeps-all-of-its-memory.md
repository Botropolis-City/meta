# 163. A hidden city keeps all of its memory

**Open. Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the hidden-window budget Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing

A hidden or unfocused city stops drawing (`SetRunnableOnUnfocused`, item 22), and its CPU is within budget: 0.4–0.9% of a core.
Its memory is not touched:

| rig | build | own when hidden | GPU when hidden | after | report |
| --- | --- | --- | --- | --- | --- |
| Core Ultra 7 255H | 0.2.2 | 3,978 MiB | 3,002 MiB | 300 s hidden | [laptop](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md) |
| Core Ultra 7 265U | 0.2.2 | 933 MiB | 988 MiB | 300 s hidden | [265U](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md) |
| Core Ultra 7 265U | r780 | 1,293 MiB | 668 MiB | 120 s hidden | 265U |

Going quiet already calls `debug.FreeOSMemory()` (`pkg/render/watching.go`, when the window stops being live), which hands back Go heap the collector has freed.
It cannot hand back what is still referenced: the draw-command queue's buffers (item 156), the kit pages and offscreen layers on the GPU (item 162), and the Go heap behind them all stay.

**The budget** ([budgets.md](../performance/budgets.md), *City*): hidden or unfocused, ≤ 1% of one core, and **own memory ≤ 256 MiB within 30 s of hiding**.
Hidden is the state the city spends most of its life in on a laptop, so this is the budget that decides what Botropolis costs a user all day.

## The fix

When the window has been hidden for a few seconds: drop the GPU images that can be rebuilt (the static layer and other offscreen layers, the kit pages of the zoom not in use, or all of them), let the draw-command queue's buffers go, and collect.
On the way back, rebuild with the loading bar budgets.md asks for before any wait, so a raise never shows a blank window.
Items 156 and 162 shrink what there is to drop; this item is about letting go of whatever is left, so it can land before or after them.

Tests: a measure test that drives a demo city to hidden and asserts the live heap and the bytes of live images fall under the budget's share within the settle time; judge it with `perf-city --hide-after`, quoting `private_dirty_mib` and `gpu_mib` 30 s after the hide.

**Re-measured after items 191–195** (265U iGPU, `458454f`, r871, [report](../performance/reports/2026-10-21-ultra7-265u-igpu-r871.md)): 30 s and 300 s after hiding, the city keeps 462–464 MiB of its own plus 315 MiB of GPU (budget ≤ 256 MiB own) and uses 7.9% of a core with spikes to 34% (budget ≤ 1%). Most of that CPU is the city laid out again on every daemon snapshot, which is item 197.
