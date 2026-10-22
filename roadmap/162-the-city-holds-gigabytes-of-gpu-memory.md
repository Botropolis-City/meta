# 162. The city holds gigabytes of GPU memory, which on integrated graphics is system RAM

**Open, in progress since 2026-10-21 in the session "item 162". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city memory budgets Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing

On integrated graphics, textures and buffers come out of system RAM and appear in no RSS or `Private_Dirty` figure; `perf-sample` reads them as `drm-total-*` from the DRM fdinfo.
The reference machine (budgets.md) is integrated graphics, so this is memory the user's laptop does not have.

| rig | build | GPU MiB settled | GPU MiB peak | own + GPU settled | report |
| --- | --- | --- | --- | --- | --- |
| Core Ultra 7 255H, Intel Arc (i915) | 0.1.7 | 939 | — | ~1.15 GB | [laptop](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md) |
| Core Ultra 7 255H, Intel Arc (i915) | 0.2.2 | 1,920–3,002 | — | 4.5–7 GB | laptop |
| Core Ultra 7 265U, Arrow Lake-U (i915) | 0.2.2 | 988 | 1,659 | 1.94 GB | [265U](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md) |
| Core Ultra 7 265U, Arrow Lake-U (i915) | r780 | 668 | 734 | 1.96 GB | 265U |

**0.1.7's 0.9 GB is itself far over budget**, so this is not only a regression: reverting would not meet it.

**What is resident**: `pkg/render/kits.go` keeps all eight kit pages of both zoom levels on the GPU whatever the zoom, each its own 2048-pixel unmanaged texture since item 70 (r765) — 128 MiB of RGBA before anything else is drawn, and more once the driver adds mipmaps or padding.
The rest is Ebitengine's offscreen images (the static layer, the shore texture sized to the island, item 85 slice 3), the window's framebuffers, and the vertex buffers the draw-command queue fills (item 156).
No one has broken the figure down yet.

**The budgets it breaks** ([budgets.md](../performance/budgets.md), *City*): **≤ 512 MiB `Private_Dirty` + GPU together**, settled with the window open, and **≤ 1 GB at any moment of start-up**.

## The fix

1. Break the GPU figure down: count every live `ebiten.Image` by size and purpose at a settled moment (a debug key, or a test through `render.NewDrive`), and compare with `drm-total-system0`.
2. Keep resident only the kit pages of the zoom in use, and load the other level's on a zoom change, a page at a time, as item 70 already does at start-up.
3. Size offscreen layers to the window, not the island, and drop what a hidden window does not need (item 163).

Tests: a measure test that counts the bytes of live images in a settled demo city, whose limit is the budget's share for textures; judge on the real display with `perf-city`, quoting `gpu_mib` with the GPU named.

**Re-measured after items 191–195** (265U iGPU, `458454f`, r871, [report](../performance/reports/2026-10-21-ultra7-265u-igpu-r871.md)): GPU alone is down to 196–331 MiB (0.2.2: 1,265–1,669), but **own plus GPU settled is 715–817 MiB against 512**. At 60 s, 96 MB of the heap is kit-page pixels kept after upload (`kits.uploadNext` → Ebitengine's `bytesPool`), and 51 MB is HarfBuzz shaping for the group-review panel.
