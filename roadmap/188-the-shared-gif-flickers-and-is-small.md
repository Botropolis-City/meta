# 188. The shared GIF flickers, and is too small

**Open. Filed 2026-10-20 (r816) from Aria's verdict on [item 168](168-share-the-city-as-a-picture-gif-or-clip.md)'s GIF. Nobody's call: she ruled the size.**

Depends on: nothing

Item 168's GIF (`botropolis/docs/screenshots/r805-item-168-workday-shared.gif`) is 720 px wide, 4 s, 60 frames.
Aria, 2026-10-20: *"Let's go 1080p. Also there's something weird with the rendering makes the whole thing look like it's flashing because the island water and such moves but in a choppy/jumpy way."*

## Diagnosis to confirm, not assumed

Two likely causes, each to be shown red before it is fixed:

1. **A palette per frame.** Item 168 encodes each frame with its own median-cut palette, so the water's and the island's colours are quantised differently from one frame to the next, and flat areas shimmer even where nothing moved. Measure: the share of pixels that change between consecutive frames over a static region (the sea far from boats, the island's grass) — near zero in the source frames, high in the GIF.
2. **15 fps.** 60 frames over 4 s is 15 fps, while the city animates at 60; the water and boats step visibly. GIF delays are in hundredths of a second, so 25 fps (4 cs) or 33 fps (3 cs) are the even choices; 50 fps (2 cs) is the most most viewers honour.

## The fix

- **1080p**: the GIF is 1920×1080 (the city re-fitted to it, as sharing does for the window), not shrunk from the window.
- **One palette for the whole clip**, built from samples of all frames, with dithering only where it does not flicker (or none), so a still region stays byte-identical frame to frame. Encode unchanged pixels as transparent against the previous frame (frame differencing), which also keeps the file small.
- **A frame rate that reads as smooth**, recorded on the city's clock as now (item 113's lockstep).
- Size: report the file size at 1080p; if it goes past what sharing sites take (GitHub's 10 MB inline limit is the useful bar), say so and propose the trade (length or fps) rather than shrinking the picture back.

Tests: a static region's pixels are identical across every frame of a recorded GIF (red on today's encoder); frame delay matches the chosen rate; the GIF's size is 1920×1080. A new GIF for Aria.
