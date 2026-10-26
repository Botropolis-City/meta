# 284. Copying a path freezes the whole city when the clipboard tool is xclip

**Open, in progress since 2026-10-26 in the session "item 284". Filed 2026-10-26 (r1120), from Aria's other laptop on 0.3.2. Nobody's call — a defect.**

Aria, 2026-10-26: *"the whole thing just froze on my work laptop after I tried to copy the path of a district."*

## What was measured, over ssh, read-only

- The city sat at 0% of a core, every one of its 28 threads waiting on a futex, the screen on.
- A process `xclip -selection clipboard` was running, reparented away from the city, holding as its stdout and stderr the write end of a pipe whose read end was the city's fd 28.
- It also held three of the city's `/dev/input/event*` descriptors, inherited.

## Why

`Control.Copy` (`pkg/control/control.go`) feeds the text to the first clipboard tool on `PATH` through `execRunner.Feed`, which runs it with `cmd.CombinedOutput()`.
`CombinedOutput` waits for the output pipe to close, not only for the process to exit.
xclip forks a child that stays to serve the selection, and the child keeps the pipe open, so `CombinedOutput` never returns.
`pkg/commands/city.go` calls `Copy` with `context.Background()`, so nothing times it out, and the city waits on it in its own loop, so the whole map stops: no frames, no input, no quit.
`xsel` behaves the same way; `wl-copy` forks too.

## The fix

1. Never wait on a clipboard tool's output pipe: give it no pipe for stdout (`/dev/null`), capture stderr only through a file or not at all, and set `cmd.WaitDelay` so a child holding a descriptor cannot hold `Wait`.
2. Give every clipboard and desktop call a short deadline, and run it off the city's loop, so no external tool can stop the map; a failure becomes a notice, not a freeze.
3. Close inherited descriptors: the child should get only stdin, stdout and stderr (the `/dev/input` descriptors it carried say others leak too; check `exec` setup for CLOEXEC on every descriptor the city opens).
4. Tests: a fake clipboard tool that forks a child holding stdout, as xclip does, returns from `Copy` within the deadline; a tool that never exits is stopped at the deadline with an error; the city's loop keeps drawing while a copy runs; and the child sees no descriptor but 0, 1 and 2.
