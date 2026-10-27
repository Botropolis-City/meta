# 302. A new session from `c` starts in the background, slowly, and exiting it lands you in your home folder

**Open, in progress since 2026-10-27 in the session "item 302". Filed 2026-10-27 (r1181), from Aria's validation of 0.3.3 (A2). Nobody's call — Aria said what she wants.**

Aria, 2026-10-27, after A1 to A6 passed: *"pressing c in a directory should attach us to the session after it starts (which is a little slow (like 6 seconds) not the end of the world, but faster would be nice). Exiting a session started in a district with 'c' puts us back in my home directory which means a prompt about trusting that folder."*
Asked what exiting should leave her with: *"The terminal closes"*.

## Where it stands

`c` acts `ActionNew` (`pkg/commands/city.go`), which runs `claude --bg` in the district's folder (`Control.New`, `pkg/control/control.go`) and returns: a building rises, and nothing opens.
Attaching is a separate step; and when she then exited the session, the terminal left her in her home folder with Claude Code asking whether to trust it, so whatever the terminal runs after the session ends starts `claude` (or a shell that does) in `$HOME`, not the session's folder. Reproduce first: which command the city's terminal runs, from `pkg/control`'s attach and the desktop's terminal (`desktop.go`), and what runs when it ends.

## The fix

1. `c` starts the session and then **attaches to it** in a terminal, as Enter on a building does, once the session is up.
2. **Exiting closes that terminal**: the terminal runs only the attach, and ends when it ends; nothing starts after it, in `$HOME` or anywhere.
3. **Faster**: measure where the ~6 s goes (`claude --bg` itself, the wait for the daemon to see the new session, the hand-off) and cut what is ours; say what is Claude Code's.
4. Tests: `c` asks the actor to start and then to attach to that session; the terminal command has nothing after the attach; and a measurement of the hand-off with a fake `claude` that answers at once.
