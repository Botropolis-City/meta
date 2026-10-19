# 148. A clip maximized on the website has its edges cropped

**Open, in progress since 2026-10-19 in the session "item 148". Filed 2026-10-19 at Aria's request. Nobody's call — a defect.**

Depends on: nothing

Aria, 2026-10-19: *"On the website, maximizing a video clips the edges. We should fix that so that it doesn't trim anything off the screen."*
The theater's player and the app window's media are styled `object-fit: cover` (`botropolis.city/src/components/Theater.astro`, `botropolis.city/src/components/AppWindow.astro`), which fills the box by cropping; when the video goes fullscreen (the player's own control, or the browser's), the screen's aspect ratio differs from the clip's and the crop cuts the strip, footer and sides of the city off.

## The fix

A maximized or fullscreen clip shows the whole frame, letterboxed on a dark background (`object-fit: contain` under `:fullscreen` / `:-webkit-full-screen`, and wherever the site has its own maximize), with nothing cropped; the inline player keeps its look. Check Safari and iOS, whose fullscreen video uses the native player.

Tests: a Playwright case that puts the player fullscreen and asserts its computed `object-fit` is `contain` (or that the rendered video rect holds the whole clip's aspect ratio inside the viewport); the inline player unchanged. A before/after screenshot for Aria.
