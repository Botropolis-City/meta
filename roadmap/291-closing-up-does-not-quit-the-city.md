# 291. Closing up from the quit prompt notes and pauses, then leaves the city open

**Fixed 2026-10-26 (`72ea643`, r1131). Filed 2026-10-26 (r1124), from Aria's use of 0.3.2. Nobody's call — a defect.**

Aria, 2026-10-26: *"Hitting enter on the close up menu doesn't actually close anything but that menu."*

*Close up* sits beside the quit prompt (`quitButton`, `pkg/render/closeup.go`) as the way to quit with notes kept.
Its panel's Enter (`closeUp.keys`) has the actor record what is open with the daemon and stop the paused sessions (`Actor.closeUp`, `pkg/commands/city.go`), then closes the panel and returns to the map: the city never quits.

## The fix

Enter in the close-up panel records, pauses what was chosen, and then quits the city, as the quit prompt's *quit* would; a failure to record or to pause shows in the panel and quits nothing.
Opened from anywhere but the quit prompt, if such a path exists, the same holds: *close up* is a way of quitting.
Since item 286 moves close-up beside the loop, the quit follows its completion, not the key press.
Tests: Enter records, pauses and quits; a recording failure keeps the panel open with the error and does not quit; a pause failure says which session and does not quit.

## Closed

A close-up that records and pauses sets `Game.closedUp`, an atomic flag, and `handleKeys` checks it after every tick's keys and leaves through `g.leave()`, the quit prompt's own path, which saves the layout.
Enter in the panel, the panel opened from the quit prompt's button, and Shift+Q with nothing open all quit that way; a failure sets nothing, so the panel (or, with nothing open, the footer) says why and the city stays.
The panel's hint now reads *enter close up and quit · esc back*.
Shown by `TestCloseUpPanel` in `pkg/render/closeup_test.go` and `TestActorCloseUp`'s "when a pause fails" in `pkg/commands/city_test.go`.
Item 286 rebases onto the flag, setting it when close-up completes beside the loop, and owns the test that the quit follows completion rather than the key press (manager, 2026-10-26).
Item 292 replaces the quit prompt's button with a centered panel, and rewrites the button case against it.
