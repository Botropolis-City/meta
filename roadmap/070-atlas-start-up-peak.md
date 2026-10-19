# 70. The atlas start-up peak holds two copies of every page, and the fix was named and never filed

**Fixed 2026-10-19 (`1af9c33`, r765). Filed 2026-09-29 out of adjudicating the eight unresolved entries in [audit-r96.md](audit-r96.md). Nobody's call — a known defect with a known fix.**

Depends on: nothing
Landed: slice 1 (`df34981`, r764).

Found inside bug 27 and looked at at r160, where the real remedy was identified, deliberately deferred as "not in this phase", and then never written down anywhere.
The phase it was deferred out of ended nine phases ago.

**The mechanism.** `assets.LoadKits` decodes all nine 2048-pixel pages before any of them is uploaded, so the decoded RGBA and the uploaded textures are alive at the same time — about 150 MB of RGBA on top of 151 MB of texture.
Measured start-up peaks: **740 MB** on Aria's desk at r156, **536 MB** on the agent's rig after handing memory back post-upload, **504 MB** at phase 18.
Handing memory back after the upload lowers the high-water mark but does not stop the peak, because both copies still exist at once.

**The fix, as named at r160:** decode and upload **one page at a time**, which cuts the peak itself rather than shortening it.
It belongs in `pkg/assets`, not the renderer.

**Why it has never hurt.** It lasts a few seconds at start-up, nobody watches it, and the machine has the headroom.
That is the honest case for leaving it, and it is why it sat unfiled for nine phases rather than being forgotten — but "nobody has seen it" is not the same as "it is not there", and the thing that made it findable was an adjudication rather than a symptom.

**What it is worth if bought:** the peak is the largest single number this program produces, roughly four times its settled cost. Item 61 established that the settled figure to quote is `Private_Dirty` or `Pss` rather than `VmRSS`, and the peak should be re-measured that way before it is priced — the 504–740 MB figures above are all `VmRSS` and so are all overstated by the ~147 MB of shared driver pages item 61 identified.

## Closed 2026-10-19

**The fix named at r160 was not enough on its own, and Aria should know the item's premise changed.**
Decoding one page at a time (slice 1, `df34981`) left the peak where it was, because Ebitengine copies anything uploaded before its loop starts and holds the copy until the first frame; `loadKits` ran before `RunGame`, so every page was still alive twice however it was decoded.
The larger cost was not in the item at all: managed, each 2048-pixel page is padded to 2050 and packed into shared 4096-pixel textures that grow by copying.

Slice 2 (`1af9c33`) puts each page on its own unmanaged texture and has the window put one page up per update inside the loop, with the clock held and the map's background (`colorVoid`) showing until the last is up — about eight updates.
Drives and tests still load every page at once.
That puts part of the fix in `pkg/render`, against the item's "not the renderer"; the manager approved it, since the deferral it works around is the renderer's.

Measured headless, on Mesa's software renderer, as `Private_Dirty` per item 61:

| | start-up peak | settled | Go heap at a collection's start |
| --- | --- | --- | --- |
| before | 1.32 GB | ~925 MB | 346 MB |
| slice 1 alone | 1.29–1.35 GB | ~915–990 MB | 283 MB |
| after | ~0.46 GB | ~490 MB | 205 MB |

The software renderer keeps textures in the process's memory, so the absolute figures on Aria's NVIDIA desk will be lower; the Go heap's fall holds on any driver.
Recorded frames of the synthetic fixture match the old ones within one colour level on every frame.

`testing/acceptance/memory_test.go` gates both parts: shared textures peak at 962 MB against its 800 MB limit, and pages put up before the loop take the heap to 274 MB against 240.
800 MB alone could not tell the second apart, because putting pages up before the loop costs only about 60 MB of `Private_Dirty` once each page has its own texture.
