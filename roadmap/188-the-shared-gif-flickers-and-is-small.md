# 188. The shared GIF flickers, and is too small

**Fixed 2026-10-20 (`5722fe5`, r823). Filed 2026-10-20 (r816) from Aria's verdict on [item 168](168-share-the-city-as-a-picture-gif-or-clip.md)'s GIF. Nobody's call: she ruled the size.**

Depends on: nothing

Item 168's GIF (`botropolis/docs/screenshots/r805-item-168-workday-shared.gif`) is 720 px wide, 4 s, 60 frames.
Aria, 2026-10-20: *"Let's go 1080p. Also there's something weird with the rendering makes the whole thing look like it's flashing because the island water and such moves but in a choppy/jumpy way."*

## Diagnosis to confirm, not assumed

Two likely causes, each to be shown red before it is fixed:

1. **A palette per frame.** Item 168 encodes each frame with its own median-cut palette, so the water's and the island's colours are quantised differently from one frame to the next, and flat areas shimmer even where nothing moved. Measure: the share of pixels that change between consecutive frames over a static region (the sea far from boats, the island's grass) — near zero in the source frames, high in the GIF.
2. **15 fps.** 60 frames over 4 s is 15 fps, while the city animates at 60; the water and boats step visibly. GIF delays are in hundredths of a second, so 25 fps (4 cs) or 33 fps (3 cs) are the even choices; 50 fps (2 cs) is the fastest most viewers honour.

## The fix

- **1080p**: the GIF is 1920×1080 (the city re-fitted to it, as sharing does for the window), not shrunk from the window.
- **One palette for the whole clip**, built from samples of all frames, with dithering only where it does not flicker (or none), so a still region stays byte-identical frame to frame. Encode unchanged pixels as transparent against the previous frame (frame differencing), which also keeps the file small.
- **A frame rate that reads as smooth**, recorded on the city's clock as now (item 113's lockstep).
- Size: report the file size at 1080p; if it goes past what sharing sites take (GitHub's 10 MB inline limit is the useful bar), say so and propose the trade (length or fps) rather than shrinking the picture back.

Tests: a static region's pixels are identical across every frame of a recorded GIF (red on today's encoder); frame delay matches the chosen rate; the GIF's size is 1920×1080. A new GIF for Aria.

## Decided while building

- **Measured, 2026-10-20**: on the workday demo, shared at 1600×1000, 0.24% of pixels change between consecutive source frames, and 17.3% changed in r805's GIF, mostly by 16 shades or fewer.
  Cause 1, the palette per frame, was nearly all of the flicker.
- **30 fps, not 25 or 50** (manager, approved with the test tree): the city ticks at 30 (`liveTPS`), not 60, so a GIF takes a frame every tick, with delays cycling 3, 3, 4 hundredths.
  Other rates would mean changing the clock.
- **The clip stays at the window's size**: only the GIF was asked for at 1080p.
- **A framed view keeps its framing** (`Scene.Reframe`): an untouched view refits to 1920×1080, and one the user panned or zoomed keeps its centre and shows the same height of the city.
  While the GIF records, the window shows the 1080p frame letterboxed, and it snaps back when the GIF ends.
- **The shade bound is a measurement**: one palette for the clip keeps each channel within 16 of 255 (`gifShade`, measured 15) when the frames share their colours, as the city's do; frames whose colours differ share the palette and cost more (42 for three unlike gradients).

## Closed

`g` in sharing mode now saves a 1920×1080 GIF, four seconds at 30 fps (120 frames), on one palette for the whole clip, with each frame after the first only the box that changed.
On the workday demo, 0.1% of pixels change between frames, against 17.3% in r805's GIF, and the file is 319 KB, far under GitHub's 10 MB, so there was no trade to propose.
`TestGIFWriter` was red on the old encoder for a still region drawn the same in every frame, for one palette, and for frames cropped to what changed; `TestShareGIF` and the acceptance test hold the size, the frame count and the delays.
Two mutations went red before the tests were trusted: the scene laid out for the window while drawn at 1080p, and `Reframe` reduced to a plain resize.
The acceptance test also caught one bug the unit rig had hidden: Ebitengine updates between layout and draw, so the first frame came at the window's size and set the clip's.
The rig now lays out in Ebitengine's order, and a GIF skips any frame not drawn at its size.

Frame: `botropolis/docs/screenshots/r820-item-188-workday-shared.gif`, named before landing; it was rendered from the code that landed at r823 and itself landed at r824.

For Aria:
- **The GIF** to judge.
- **The window jumps while a GIF records**: it shows the 1080p frame letterboxed for the four seconds, then snaps back to its own fit.
