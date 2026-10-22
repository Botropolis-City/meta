# 162. The city holds gigabytes of GPU memory, which on integrated graphics is system RAM

**Open, in progress since 2026-10-22 in the session "item 162". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city memory budgets Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing
Landed: slice 1 (`b2ec8b6`, r886).
Landed: slice 2 (`c47a2a3`, r884).
Landed: slice 3 (`d100abf`, r889).
Landed: slice 4 (`e6bde10`, r905).

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

**What it was, and what landed** (2026-10-22).
The 96 MB was not the pool: Ebitengine keeps an image's written pixels on the CPU until the image is first drawn from, and z2 is drawn only from zoom 1.98, so its six pages stayed on the heap whole.
Slice 1 draws a pixel from each page as it goes up, and sends pages in 64-row strips so the pool keeps at most 31 × 512 KiB; a test fails when the build's Ebitengine is not v2.10.2, which those facts were read from.
Slice 2 clips text by doubling and halving a prefix, memoised, so the group-review panel no longer fills the shaping cache with near-whole rows.
Slice 3 keeps resident only the kit level the camera picks, puts the other up a page an update on a zoom across the threshold, and lets a level go after 300 updates unpicked.
Slice 4 is the guard the Tests line asks for, made whole instead of partial (the roadmap manager, 2026-10-22): a sum of the city's own images would miss Ebitengine's, which is where the 96 MB hid, so `TestSettledMemory` gates a settled metropolis under Xvfb, where the software renderer's textures are the process's own memory, at 512 MiB of `Private_Dirty`.
On the way, the night draw-command ceiling went to main's own worst, 42, and frame work is counted from the city's first drawn frame.

**Measured after slices 1–3** (265U iGPU, `d100abf`, r889, [report](../performance/reports/2026-10-22-ultra7-265u-igpu-item-162.md)), on the metropolis demo at fit: **own plus GPU settled 355 MiB** (76 own, 279 GPU), against 689 at r871 (310 and 379); Go heap live 24 MB against 141; under Xvfb 250 MiB against 528.
**Owed:** the same on the real history, where the budget is set, through a scratch daemon on a copy of the state directory; and at full zoom. Both need a focused window, and the desk was in use, so the roadmap manager is having them run with items 161 and 163's re-measure.

**Measured on the real history at r905** (`e6bde10`, [report](../performance/reports/2026-10-22-ultra7-265u-igpu-r905.md)): **met at fit**, 398–400 MiB own plus GPU (r871: 715–817); **not at full zoom**, 618–620 MiB, about 110 over 512. The metropolis meets both (342 and 481).
