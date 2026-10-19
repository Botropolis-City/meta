# 148. A clip maximized on the website has its edges cropped

**Fixed 2026-10-19 (botropolis.city `6f60d23`, r29). Filed 2026-10-19 at Aria's request. Nobody's call — a defect.**

Depends on: nothing

Aria, 2026-10-19: *"On the website, maximizing a video clips the edges. We should fix that so that it doesn't trim anything off the screen."*
The theater's player and the app window's media are styled `object-fit: cover` (`botropolis.city/src/components/Theater.astro`, `botropolis.city/src/components/AppWindow.astro`), which fills the box by cropping; when the video goes fullscreen (the player's own control, or the browser's), the screen's aspect ratio differs from the clip's and the crop cuts the strip, footer and sides of the city off.

## The fix

A maximized or fullscreen clip shows the whole frame, letterboxed on a dark background (`object-fit: contain` under `:fullscreen` / `:-webkit-full-screen`, and wherever the site has its own maximize), with nothing cropped; the inline player keeps its look. Check Safari and iOS, whose fullscreen video uses the native player.

Tests: a Playwright case that puts the player fullscreen and asserts its computed `object-fit` is `contain` (or that the rendered video rect holds the whole clip's aspect ratio inside the viewport); the inline player unchanged. A before/after screenshot for Aria.

## Closed

Fixed in botropolis.city `6f60d23`, deployed by the `site` run 39297288540, which went green.
Video in an app window is now `object-fit: contain` everywhere, letterboxed on the page's dark background, so fullscreen shows the whole frame.
Still images keep `cover`, since they cannot be maximized.
The site has no maximize of its own, and the theater's player is its only playable video, so that one rule is the whole fix.
Every clip is 1920×1080, the window's 16:9 shape, so the inline player looks exactly as before.
A clip of another shape would get bars instead of losing its edges.
iOS Safari's fullscreen is the native player, which ignores page CSS and always shows the whole frame.
Desktop Safari applies the same `contain` rule.

Tests in `testing/acceptance/site/page.spec.ts`: the player is `contain` inline at 390, 768, 1280 and 1920 wide and keeps the 16:9 shape; fullscreen, it is `contain` on the dark background; every clip the theater offers is 16:9.
Aria approved the before/after fullscreen and inline screenshots on 2026-10-19.

Deviation, for Aria: the item asked for the inline player to keep `cover`.
At the manager's request it is `contain` inline too.
For today's clips it looks identical,
and a future clip of another shape is never trimmed.
