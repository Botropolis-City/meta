# 302. A new session from `c` starts in the background, slowly, and exiting it lands you in your home folder

**Fixed 2026-10-27 (`1878040`, r1188). Filed 2026-10-27 (r1181), from Aria's validation of 0.3.3 (A2). Nobody's call — Aria said what she wants.**

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

## Closed

`c` now starts the session and then attaches to it, as resume and fork do.
Every terminal the city opens on a session starts in that session's folder: from the action (Enter, the finder, the TUI, `c`, resume, fork, open), or else from the live job's cwd in `claude agents`.
`TestNewSessionOpens` runs the real exec path with a fake `claude` and a fake terminal, and checks the terminal runs exactly `claude attach <job>` in the district's folder; with the folder fix mutated away it fails.

**Deviation, ruled by Aria on 2026-10-27: the terminal does not close on exit.**
That part is Claude Code's behaviour.
When an attached session detaches from inside, and stdin and stdout are terminals, `claude attach` (2.1.310) relaunches itself as `claude agents`, the agent view, in its own working directory.
That was the trust prompt in `$HOME`.
Nothing of ours runs after the attach.
Claude Code has no switch for it: `CLAUDE_CODE_DISABLE_AGENT_VIEW=1` also makes `attach` refuse.
Aria ruled for the session's folder with no prompt, and no wrapper around `attach`; revisit if Claude Code gains a switch.

**Speed:** with a `claude` that answers at once, the city's hand-off from `c` to the terminal opening takes about 7 ms (`BenchmarkNewSessionHandOff`).
The roughly 6 seconds are `claude --bg` itself, which is Claude Code's.
