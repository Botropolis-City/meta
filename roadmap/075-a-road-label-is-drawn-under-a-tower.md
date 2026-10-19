# 75. A road's label is drawn under the tower beside it

**Fixed 2026-10-18 (`5b304e9`, r628). Filed 2026-10-10 (r376), from the demo frames. Nobody's call — a defect.**

The traffic label `1 file` on the avenue between thistledown and copperleaf is drawn before thistledown's tower, so the tower covers its right half.
Labels are chrome and should draw over the city, or move off whatever stands on them, the way the tower signage in [later.md](later.md) does.

Seen in `metropolis/overview.png`, `metropolis/plain.png` and `metropolis/sidebar.png` (around (1185, 487) at 1920×1080), and in `metropolis/flyover.mp4` whenever that avenue is in shot.
The flat projection (`workshop/flat.png`) has a road label too, at (743, 388), and it is not covered there, so the fault is in the isometric draw order rather than in placing the label.

## Closed

Fixed 2026-10-18 by [item 102](102-badges-signs-and-line-labels-overlap.md)'s slice 4 (`5b304e9`, r628), which moved road tags out of the static layer, painted under everything, into the label layout drawn after the depth pass.
Found fixed on 2026-10-19 when the item was started: metropolis at 1920×1080 on r673 draws its `1 file` tag whole and on top.
The city has moved since r376, so no tower now stands right beside that tag; the frame shows the tag reads, and the draw order shows the fault is gone.

Guard (manager, 2026-10-19), `92abbd8`, r682: `TestRoadTagsDrawOverTheCity` in `botropolis/testing/acceptance/labels_test.go`.
The map numbers what it issues as it issues it — each world sprite in `drawSprite` and `kitRising`, each road tag where `drawMapLabels` draws it — and the workshop demo must draw no tag before a world sprite.
Taking tags back out of the layout was already caught, by 102's overlap test, which needs a tag; keeping them in the layout but drawing it before the buildings passed every test until this one ("Should be zero, but was 1").

Not done, in case a pixel-level guard is ever wanted: a test that stands the tallest building under a workshop road tag and counts the tag's ink pixels against bare ground, with a precondition, labels hidden, that the building does change the pixels there.
ebiten panics on `ReadPixels` unless a game loop is running, so it would need its own `TestMain` running the tests inside `ebiten.RunGame` under Xvfb, behind a build tag, called from `make test-integration`.
The manager passed on it as too much machinery for a guard on a bug already fixed; the draw-order test above stands in for it.
