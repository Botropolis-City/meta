# 291. Closing up from the quit prompt notes and pauses, then leaves the city open

**Open. Filed 2026-10-26 (r1124), from Aria's use of 0.3.2. Nobody's call — a defect.**

Aria, 2026-10-26: *"Hitting enter on the close up menu doesn't actually close anything but that menu."*

*Close up* sits beside the quit prompt (`quitButton`, `pkg/render/closeup.go`) as the way to quit with notes kept.
Its panel's Enter (`closeUp.keys`) has the actor record what is open with the daemon and stop the paused sessions (`Actor.closeUp`, `pkg/commands/city.go`), then closes the panel and returns to the map: the city never quits.

## The fix

Enter in the close-up panel records, pauses what was chosen, and then quits the city, as the quit prompt's *quit* would; a failure to record or to pause shows in the panel and quits nothing.
Opened from anywhere but the quit prompt, if such a path exists, the same holds: *close up* is a way of quitting.
Since item 286 moves close-up beside the loop, the quit follows its completion, not the key press.
Tests: Enter records, pauses and quits; a recording failure keeps the panel open with the error and does not quit; a pause failure says which session and does not quit.
