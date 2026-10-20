# 167. The command line has spread out, and ships no man pages

**Open, in progress since 2026-10-20 in the session "item 167". Filed 2026-10-20 (r784) at Aria's request, on the road to 1.0.0. Aria's call — the shape the analysis proposes.**

Depends on: nothing

Ruling on what 1.0.0 promises ([item 149](149-what-1-0-0-promises.md)), Aria, 2026-10-20: *"I think my biggest concern with the commands is how many there are. … even if we just wrap a claude thing, asking a user to do a claude command feels like a leaky abstraction. So it's not that I necessarily want to remove commands that have a function. I just want to do a full analysis of the commands that we have and the flags and make sure we haven't spread out too much. That way end users can actually learn and memorize. We also should be creating and shipping man pages with all of this if we don't already."*
Today `botropolis` has 19 commands (`attach`, `bar`, `city`, `completion`, `doctor`, `events`, `find`, `help`, `install-hooks`, `new`, `notify`, `prune`, `resume`, `rm`, `shell-init`, `status`, `stop`, `tui`, `version`), and every config key is also a global flag on every one of them (about 40), so `botropolis status --help` lists city-drawing flags. No man page is built or packaged.

## Slice 1 — the analysis, for Aria to rule on

A written review (in the item, with a one-page table): every command and flag, what it does, who uses it (person, script, the city, a systemd unit, the hook), what it overlaps, and a proposed shape that a person can learn — grouping (for example session verbs under one noun, setup under another), names that say what they do, which global flags belong only to the commands that read them, and which config keys need no flag at all. Wrapping `claude` is fine, and is the point: a person should never need to drop to `claude`. Nothing is removed for having a function; overlaps are merged, not deleted. Show the proposed `--help` for the root and each command. No code changes until Aria rules.

## Slice 2 — the shape she picks, plus man pages

Implement it, keeping old names working with a deprecation note for the rest of 0.x so scripts have time; man pages generated from the command tree (`botropolis(1)`, one per command, and `botropolis-config(5)` for the config file), installed by every package (deb, rpm, Arch, Homebrew) and checked by the package install tests; `make man` builds them, and a test fails when a command has no page.

Item 149's golden file for the command tree waits for this item, so 1.0 promises the shape Aria chose rather than today's.
