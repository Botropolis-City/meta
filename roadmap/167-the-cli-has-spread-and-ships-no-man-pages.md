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

## Slice 1: the analysis (2026-10-20, r784)

Read from the built binaries' `--help` and from `botropolis/pkg/cli`, `pkg/config`, `pkg/control`, `pkg/shellinit`, `pkg/app` and `packaging/`.

### What there is today

| command | does | who runs it | overlaps | proposed |
| --- | --- | --- | --- | --- |
| *(none)* | opens the city; `--tui` opens the table instead | person, the desktop entry | `city`, `tui` | stays: bare `botropolis` is the city |
| `city` | opens the city; carries the frame flags and `--signage` | person, `botropolis-demo`, acceptance tests | bare `botropolis` | stays, with one user flag; frame flags go to dev builds |
| `tui` | the live session table, with keys to attach, stop and remove | person | `--tui`, `status` | folds into `status --live`; `tui` and `--tui` deprecated |
| `status` | prints the session table once; `--json`, `--all`, `--direct` | person, scripts | `tui` | stays, gains `--live` |
| `find` | searches what was said; with no words opens the finder in the city | person, a desktop hotkey | — | stays |
| `new` | starts `claude --bg` in a directory and prints its job id | person, the shell integration | — | stays |
| `attach` | opens a **new terminal window** on a background session | person | `resume`; the shell integration uses `claude attach` instead | attaches **here** from a terminal, a new window otherwise; resumes a resting session itself |
| `resume` | `claude --bg --resume`, then `attach` | person | `attach` | folds into `attach`; deprecated alias |
| `stop` | `claude stop` | person | — | stays |
| `rm` | `claude rm`, and the ledger forgets it | person | `prune` | stays, gains `--older-than` |
| `prune` | removes resting sessions older than a cutoff, and empty ones after an hour | person | `rm` | folds into `rm --older-than`; deprecated alias |
| `install-hooks` | writes the hook into `~/.claude/settings.json`; `--remove`, `--dry-run` | person, once | `shell-init`, the postinstall hint | becomes `setup` |
| `shell-init` | prints the integration that makes a plain `claude` a background session | every shell's rc file, `packaging/botropolis.bash` | `completion` | stays, unrenamed, and also loads completions |
| `completion` | cobra's default: prints completions for four shells | packages (Homebrew's formula), person rarely | `shell-init` | stays for packagers, hidden from `--help` |
| `doctor` | checks the daemon, hooks, terminal, `claude`, harnesses, display | person | — | stays |
| `events` | prints the daemon's event log; `--since` | person, diagnosing | — | stays |
| `bar` | one line for a status bar; `--format`, `--watch` | waybar and its kin | — | stays |
| `notify` | desktop notifications when a session needs you | `botropolis-notify.service` | — | stays |
| `version` | prints the version | person | `--version` | removed before 1.0, as ruled in item 149 |
| `help` | cobra's help | person | `--help` | stays |

19 commands become **13 visible**, plus `help`; nothing with a function is lost, and every old name keeps working through 0.x with a deprecation note.

| flags | count | where today | who reads them | proposed |
| --- | --- | --- | --- | --- |
| `--config`, `--home`, `--socket` | 3 | global, on all four binaries | every command, the daemon, the hook, tests, the demo | stay global: they say *which* city |
| the city's settings: `--shuttered_days`, `--overgrown_days`, `--render_scale`, `--reduced_motion`, `--liveliness`, `--district_type`, `--stats`, `--daily_budget_usd`, `--detail`, `--usage_refresh`, `--group_lines`, `--labels` | 12 | global, on all four binaries | the city only (`stats` also the daemon) | no flag each: one global `--set key=value`, repeatable, for any key |
| the city's keys: `--find_key`, `--find_copy_key`, `--find_show_key`, `--new_session_key`, `--explain_key`, `--triage_key`, `--journal_key`, `--stream_key`, `--city_plan_key`, `--labels_key`, and `--journal_hours` | 11 | global, on all four binaries | the city only | no flag each: `--set` covers them |
| `--projection` | 1 | global | nothing: deprecated | removed before 1.0, as ruled in item 149 |
| frame tooling: `--screenshot`, `--keys`, `--hover`, `--record`, `--fps`, `--seconds`, `--script`, `--headless`, `--window`, `--signage` | 10 | `city`, and all but `--signage` on the root too | `botropolis-demo`, `tools/measure-render`, acceptance tests, `make gif` | hidden, unpromised, and in dev builds only (below) |
| `--tui` | 1 | root | person, README | deprecated for `status --live` |
| per-command: `status --all --json --direct`, `find --limit --tool-output`, `events --since`, `bar --format --watch`, `install-hooks --remove --dry-run`, `prune --older-than --dry-run`, `resume --dir` | 13 | their commands | as their commands | stay, moving with their command |

### What spread, and where it leaks

1. **Every config key with a flag is a global flag on every binary.**
   `botropolis status --help`, `botropolisd --help` and even `botropolis-hook --help` list 27 flags about drawing the city, so the useful ones (`--json`, `--all`) sit under a page of key bindings.
   Four keys have no flag at all (`terminal`, `hook_command`, `codex_home`, `global_shortcut`), so the flag set is neither complete nor small.
   `--set key=value` is one flag to learn, reaches every key, uses the file's own key name, and the man page `botropolis-config(5)` lists the keys once.
   `BOTROPOLIS_<KEY>` environment variables already work and stay.
2. **Two spellings.** Settings flags are snake_case (`--daily_budget_usd`), command flags kebab-case (`--dry-run`, `--older-than`).
   With the per-key flags gone, every flag left is kebab-case, and the snake_case name survives only where it belongs, as a key in the file.
3. **Three ways to open the table and two to open the city:** `tui`, `--tui` and `status` print the same rows, and `city` is bare `botropolis`.
4. **`attach` and `resume` are one intent**, "open that session", split by whether it happens to be resting, which the person should not have to know.
5. **`rm` and `prune` are one verb**, one session or many.
6. **The leak to `claude`:** `botropolis attach` always opens a *new* window, so the shell integration calls `command claude attach "$id"` to attach in the terminal you are in.
   There is no botropolis verb for "attach here", so over SSH, or anywhere without a desktop, the person has to drop to `claude attach`.
   Proposed: `attach` attaches in the current terminal when run from one, and opens a window when not (a launcher, a hotkey), or with `--new-window`.
   The shell integration then calls `botropolis attach`.
7. **Setup is three steps in three tools** (`systemctl`, `install-hooks`, `shell-init`), and the postinstall hint and Homebrew caveats spell out all three.
   `botropolis setup` installs the hooks, checks the daemon is running and, if not, prints the one line that starts it, and prints the shell line for `$SHELL`.
8. **Smaller defects found on the way**, fixed in slice 2 whatever the shape:
   - `status --help` renders `--json claude agents`, because pflag reads a back-quoted word in a usage string as the value's name;
   - the README names `BOTROPOLIS_PARKED_DAYS`, which no key reads (it is `BOTROPOLIS_SHUTTERED_DAYS`), and lists 12 of the 30 keys;
   - the city can fork a session and the command line cannot, and `claude logs` has no botropolis equivalent — both gaps, not proposed here, since this item merges rather than adds.

**Kept deliberately:** `shell-init` is not renamed.
It runs from every user's rc file on every shell start, so a deprecation note there would print on every new terminal, and removing it at 1.0 would break every shell that has it.
It becomes the one line a person adds, and loads completions as well, so `completion` is needed only by packagers.

### Frame tooling: out of release builds (Aria, 2026-10-20, through the manager)

Aria: the frame and test flags are hidden and unpromised, and *"we should create a way to compile with and without these to make the final result lighter for consumers but allow them to exist in a dev or debug build."*

- **A build tag, `devtools`.** The flags, the recorder, the scripted driver, the pointer parking and the Xvfb launcher move behind `//go:build devtools`, with an empty stub without it.
  `make build`, CI's packages and the release build without it; `make build-dev`, `make demo-tool`, `make gif`, the acceptance tests and `tools/measure-render` build with it.
- **It is lighter in surface, not in bytes.** Measured with `go tool nm -size` at r784: the tooling's own code is about 30 KB of a 53.7 MB `botropolis`, under 0.1%, because the PNG encoder stays for `p`.
  The gain is that release users never see, can never script against, and 1.0 never promises the flags.
- **The risk is testing a binary that does not ship.** The acceptance tests need the tag, so two guards keep the release honest: the package install tests run the untagged binary, and an acceptance test builds it untagged and asserts that `city --screenshot` is an unknown flag, so a tag that strips nothing fails.

### A screenshot or recording for people (for Aria to rule)

`p` already saves the frame as a PNG to `~/Pictures` (or `~`), and says where, in every build.
Three shapes, from least to most:

1. **Leave `p` as it is**: it is already in the key reference, and goes in the man page too.
2. **Add a recording:** a key starts and stops recording (not `shift+r`, which turns the heading as `r` does; the key is the item's to choose against the key reference) into an animated GIF in the same folder, with `image/gif` from the standard library, so no ffmpeg; a chip shows it is recording.
3. **Either, with a "for sharing" choice**: a capture with labels and the spend hidden.
   This is the exposure this repository paid for — `docs/botropolis.gif` showed a project name, MCP vendor names and a real daily spend for nine days — and a person posting their city meets the same thing.

Recommended: 1 now in this item, and 2 with 3 as its own item if she wants it, since a recorder is new work, not a merge.

### The proposed shape

Global flags on every command and on `botropolisd` and `botropolis-hook`: `--config`, `--set`, `--home`, `--socket`, `-h`, and `-v`/`--version` on the root.

```
$ botropolis --help
Every Claude Code session on the machine, as a city.

With no command, botropolis opens the city.

Usage:
  botropolis [command]

Sessions:
  new         Start a session in the background and print its id
  attach      Open a session in this terminal, resuming it if it is resting
  stop        Stop a session; its conversation is kept
  rm          Delete a session, or every resting one older than a cutoff
  status      List the sessions; --live keeps the table open
  find        Find sessions by what was said in them

The city:
  city        Open the city

Setting up and checking:
  setup       Install the hooks and say what else is missing
  doctor      Check the daemon, the hooks, a terminal, claude and the display
  events      Print the daemon's log of what needed you, errored or ended

For other programs:
  bar         One line for a status bar, as waybar JSON or text
  notify      Send a desktop notification when a session needs you
  shell-init  Print the shell integration for your rc file

Flags:
      --config file        the config file to read and save (default ~/.config/botropolis/config.toml)
      --set key=value      set a config key for this run; repeatable (see botropolis-config(5))
      --home dir           the home directory holding .claude (default $HOME)
      --socket path        the daemon's socket
  -h, --help               help for botropolis
  -v, --version            print the version

See botropolis(1), and "botropolis help <command>".
```

```
$ botropolis new --help
Start a session in the background in <dir>, optionally with a first prompt,
and print its id. A plain claude does this for you once shell-init is in your
rc file.

Usage:
  botropolis new <dir> [prompt...]
```

```
$ botropolis attach --help
Open a session. In a terminal it attaches there; from anywhere else, or with
--new-window, it opens a terminal. A resting session is resumed first, in its
own directory unless --dir says otherwise.

Usage:
  botropolis attach <id>

Flags:
      --dir dir        resume a resting session in this directory
      --new-window     open a new terminal even when run from one
```

```
$ botropolis stop --help
Stop a session. Its conversation is kept, and attach brings it back.

Usage:
  botropolis stop <id>
```

```
$ botropolis rm --help
Delete a session, or with --older-than every resting session with no
activity for that long and every empty one that sat for an hour.

Usage:
  botropolis rm <id>...
  botropolis rm --older-than <duration>

Flags:
      --older-than duration   delete every resting session quiet for this long, e.g. 168h
      --dry-run               list what would be deleted and change nothing
```

```
$ botropolis status --help
List the sessions: one row per live one, or with --all the resting ones too.
With --live the table stays open and updates; j and k move, enter attaches,
s stops, x deletes, q quits.

Usage:
  botropolis status

Flags:
  -a, --all       include resting sessions
  -l, --live      keep the table open, live
      --json      one JSON object per line per session (promised: see botropolis(1))
      --direct    read ~/.claude without asking the daemon
```

```
$ botropolis find --help
Find sessions by what was said in them; every word must appear in one passage.
With no words it opens the finder in the city, so it can be bound to a key:
see botropolis-find(1) for GNOME, KDE, macOS and i3.

Usage:
  botropolis find [words...]

Flags:
  -n, --limit n         how many sessions to print, 0 for all (default 10)
      --tool-output     also search tool output
```

```
$ botropolis city --help
Open the city. botropolis alone does the same. A second one brings the first
forward. Settings live in the config file, in the city's settings panel (s),
or for one run in --set.

Usage:
  botropolis city
```

```
$ botropolis setup --help
Install the hooks in ~/.claude/settings.json, check the daemon is running,
and print the line for your shell's rc file. Safe to run again.

Usage:
  botropolis setup

Flags:
      --dry-run   print what would change and change nothing
      --remove    take the hooks out again
```

```
$ botropolis doctor --help
Check the daemon, the hooks, a terminal, the claude CLI, the harnesses and the
display, and say how to fix what is missing.

Usage:
  botropolis doctor
```

```
$ botropolis events --help
Print the daemon's log: what needed you, errored, merged, started or ended.

Usage:
  botropolis events

Flags:
      --since duration   how far back to list (default 24h)
```

```
$ botropolis bar --help
One line for a status bar such as waybar: the sessions that need you, as
waybar JSON (promised: see botropolis(1)) or text.

Usage:
  botropolis bar

Flags:
      --format waybar|text   (default waybar)
      --watch                print a new line whenever something changes
```

```
$ botropolis notify --help
Send a desktop notification whenever a session starts needing you. The
botropolis-notify user service runs it; you need not.

Usage:
  botropolis notify
```

```
$ botropolis shell-init --help
Print the shell integration, which makes a plain claude a background session
and loads completions. Add one line to your rc file:

  bash  ~/.bashrc                    eval "$(botropolis shell-init bash)"
  zsh   ~/.zshrc                     eval "$(botropolis shell-init zsh)"
  fish  ~/.config/fish/config.fish   botropolis shell-init fish | source

Usage:
  botropolis shell-init bash|zsh|fish
```

Deprecated through 0.x, each printing one line to stderr naming its replacement, and removed at 1.0.0 with a *Removed* entry in the changelog: `tui` and `--tui` (`status --live`), `resume` (`attach`), `prune` (`rm --older-than 168h`), `install-hooks` (`setup`), `version` (`--version`), every per-key flag (`--set key=value`), and `--projection`.

### Man pages

Generated from the command tree with `github.com/spf13/cobra/doc` (Apache-2.0, with go-md2man, MIT): `botropolis(1)` and one `botropolis-<command>(1)` each, `botropolisd(1)`, `botropolis-hook(1)`, and `botropolis-config(5)` from the same list of keys that item 149's golden file reads, with each key's values, default and environment variable.
`make man` writes them to `man/`, git-ignored; nfpm installs them under `/usr/share/man/man1` and `man5`, which covers the deb, the rpm and the Arch package, and the Homebrew formula runs the same generator and calls `man1.install`.
A unit test walks the tree and fails on a command with no page, and the package install tests run `man -w botropolis-status`.

### For Aria to rule on

1. The shape above, as a whole, or with changes.
2. `tui` into `status --live`, or keep `tui` as its own command (14 visible).
3. `prune` into `rm --older-than`, or keep `prune` (14 visible): `prune` is a familiar word from git and docker.
4. Whether `setup` starts the daemon itself (`systemctl --user enable --now botropolisd`, or `brew services start`), making setup one command, or only says how.
5. The in-app capture: 1, 2 or 3 above.

## Aria's ruling (2026-10-20, through the roadmap manager)

1. **The shape above, all of it:** 13 visible commands, `--set key=value` in place of the per-key flags, `attach` in this terminal absorbing `resume`, old names deprecated through 0.x and removed at 1.0.0 with *Removed* entries, `shell-init` keeping its name, man pages in every package, and the frame tooling behind the `devtools` build tag with its guard.
2. **`tui` folds into `status --live`.**
3. **`prune` folds into `rm --older-than`.**
4. **`setup` starts the daemon itself** (`systemctl --user enable --now botropolisd`, or `brew services start botropolis`), and says exactly what it ran.
5. **In-app capture is its own item**: a sharing mode offering PNG, GIF and a clip, filed by the manager. `p` stays as it is here.

The `status --help` rendering and the README's environment variables and key list are fixed in slice 2 as well.
