# 282. The wheel cannot always reach Skyline, and the City Plan cannot be zoomed

**Open, in progress since 2026-10-26 in the session "item 282". Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria said what she wants.**

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: *"I should be able to zoom all the way out into the top view. Currently, I need to hit f, and then I can zoom out into it. I should be able to just zoom all the way out and then hit a debounce on zooming out for the last level ... Also, I should be able to zoom all the way out to the skyline view. It's weird that the only way to get there is hitting f because I can't manually zoom that far. Also, I should be able to zoom in on the top down view without going straight into the normal view. Some of the things are hard to see with lots of sessions."*

What exists: the wheel steps through `ZoomSteps` (`pkg/city/camera.go`) and is meant to stop at `SkylineZoom` (`pkg/city/cityplan.go`), and wheeling out at Skyline after the wheel has rested `PlanDebounce` (350 ms) opens the City Plan, the flat top-down view (`pkg/city/scene.go`; item 106).
So two of her asks are already the design and one is missing:

1. **The wheel stops short of Skyline** on her city: she reaches Skyline only with `f`, so the plan's debounce never starts. Reproduce on a big island (item 270's staged city and an ordinary one): the wheel ladder's last step must reach `SkylineZoom` whatever the island's size, since Skyline's zoom is computed from the island and can lie below the ladder's last step.
2. **Zooming inside the plan**: today any wheel-in while the plan is open closes it, and wheel-out does nothing (`pkg/city/cityplan_test.go` holds both). The plan gets its own zoom, with the wheel zooming it about the pointer, and a wheel-in at the plan's closest zoom, after the same debounce, returns to the map.

## The fix

Tests, data-driven over island sizes: wheeling out from any zoom reaches Skyline; at Skyline, a rested wheel-out opens the plan; in the plan, wheel-in and out zoom it about the pointer; at the plan's closest zoom, a rested wheel-in returns to the map.
Flip the two `cityplan_test.go` cases that hold the old wheel.

## Answered while building

- **The fix's shape** (session's, approved by the manager, 2026-10-26): reproduced on any island whose Skyline zoom lies below the ladder's last step (0.25): the step below that is now Skyline. The plan zooms in steps 1, 1.5, 2, 3, 4, 6 and 8 about the pointer, decides compact badges from those in view, pans by drag held inside the window (right and middle drags too, with item 279), reopens at its widest, and from its closest zoom a rested wheel-in returns to the map at Skyline with the pointed place kept.
