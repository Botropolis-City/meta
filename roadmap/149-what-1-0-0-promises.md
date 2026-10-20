# 149. What 1.0.0 promises is written nowhere, and nothing fails when it changes

**Open, in progress since 2026-10-20 in the session "item 149". Filed 2026-10-19 (r748), at Aria's request, on the road to 1.0.0. Nobody's call: Aria ruled on the list on 2026-10-20.**

Landed: slice 1 (`89df7a6`, r760).
Landed: slice 2 (`2f26c80`, r808).

Under Semantic Versioning, 1.0.0 is a promise: what people depend on does not break without a 2.0.0.
Botropolis has never said what that is.
This item writes the list, makes each entry checkable, and fixes the two places where today's code would break the promise the first time it changed.

Aria, 2026-10-19, asked for it after the status update proposed it as one of the six things 1.0.0 needs.

## The surface, as it stands at r748

| surface | where it is defined | what depends on it |
| --- | --- | --- |
| the commands: `attach`, `bar`, `city`, `doctor`, `events`, `find`, `install-hooks`, `new`, `notify`, `prune`, `resume`, `rm`, `shell-init`, `status`, `stop`, `tui`, `version`, and their flags | `botropolis/pkg/cli/*.go` | scripts, shell init, muscle memory |
| `status --json`, one object per session | `botropolis/pkg/cli/status.go` | anything that parses it |
| the config keys in `config.toml` (`home`, `socket`, `terminal`, `hook_command`, `shuttered_days`, `overgrown_days`, `codex_home`, `projection`, `render_scale`, `reduced_motion`, `liveliness`, `daily_budget_usd`, `detail`, `usage_refresh`, `group_lines`, `labels`, `district_type`, `stats`, `global_shortcut`) and their values | `botropolis/pkg/config/config.go` | every user's file |
| the hook command, `botropolis-hook`, written into Claude Code's settings | `botropolis/pkg/hooks/hooks.go` | every installed hook, which outlives an upgrade |
| `stats.db` | `botropolis/pkg/stats/store.go` | statistics that cannot be recovered once their transcripts are pruned |
| `layout.json`, `ledger.json`, `frame.toml` | `botropolis/pkg/city/layout.go` and their packages | the city's arrangement, packed sessions |
| the package names and fixed release names | `botropolis/packaging/`, `botropolis/tools/release-aliases` | the website's install links, the APT, RPM and Homebrew repositories |

The daemon protocol (`botropolis/pkg/proto/proto.go`) is internal: one package ships both ends.
But see the second defect.

## Two defects the promise would expose

1. **A `layout.json` of another version is thrown away in silence.**
   `botropolis/pkg/city/layout.go:172` returns `NewLayout()` when `layout.Version != layoutVersion`, so the first bump of `layoutVersion` would reset every user's districts and slots with no message.
   `stats.db` already does this right (item 116: `readable_from` and `written_by` in its `meta` table, and a newer store refused by name).
   The layout and the ledger want the same: migrate forward, refuse a newer file by name, never reset.
2. **The client and the daemon never exchange versions.**
   `Request` carries an `op` and nothing else, so after a package upgrade a still-running old daemon answers a new client, and a changed response shape fails in whatever way it happens to fail.
   The fix is a version in the first exchange, and a client that says "restart the daemon: it is <old>, this is <new>" rather than misbehaving.

## The fix

1. **`docs/compatibility.md` in botropolis**: the list above, what each promise covers (removing or renaming is breaking; adding is not), and what is deliberately left out: the protocol, the look of the map, the art, the TUI's layout.
   Linked from `DESIGN.md`'s index and the README.
2. **A golden test per surface**, in `testing/acceptance/`, so a change to the surface fails until its golden file changes in the same commit:
   - the command tree with every flag, its type and default, walked from the root command;
   - the `status --json` keys;
   - the config keys and their accepted values;
   - the `stats.db` schema from `sqlite_master`, and `ReadableFrom`;
   - the layout and ledger versions;
   - the fixed release names, which `release_aliases_test.go` partly pins today.
3. **A version check that reads `VERSION`**: from 1.0.0 on, `make version-check` fails when a golden file changes in a removing way and the major version did not rise.
   Adding a key or a flag passes.
   Whether "removing" is computed (the golden files are sets, so removal is a set difference) or declared in the changelog is the session's proposal to make.
4. **The two defects above**, each red then green.

## Whose call

Aria decides the list: anything above she would rather not promise, and anything missing.
The rest is known work.

## Answered while building

- **Slice 1 is the two defects** (Aria, 2026-10-19, through the planning session and confirmed to the manager): the layout file reset in silence (`botropolis/pkg/city/layout.go:172`) and the missing client/daemon version exchange start now; the list and its golden tests wait for her ruling on what is on it.

**Aria on the frame** (2026-10-19): a mismatch should stop the map rather than show a chip — [item 152](152-an-out-of-sync-daemon-stops-the-map.md).

## Aria's ruling on the list (2026-10-20)

Interviewed by the roadmap manager:

- **Commands and their flags are promised**, every one, except **`version`, which is removed before 1.0**: `botropolis --version` stays and is promised.
- **Machine-readable output:** `status --json` and **`bar`'s JSON** (its text, tooltip and class names, which status bars parse) are both promised; `bar` was missing from the table.
- **Config keys:** every current key and its values, except **`projection`, which is removed before 1.0** (deprecated since the top-down view went), so 1.0 does not promise a dead key.
- **Data files** (`stats.db`, the layout file, the session ledger `sessions.json` — not `ledger.json` as the table says): **readable forward and never lost**. Any later 1.x reads every earlier 1.x file and migrates it, and a newer file is refused by name, never reset; the files' internal shape is not promised.
- **Install surfaces:** the APT, RPM and Homebrew package names, the fixed release asset names, the systemd units (`botropolisd.service`, `botropolis-notify.service`) and the hook command `botropolis-hook` are promised. **The AUR package names (`botropolis`, `botropolis-bin`) are not**: they are published to the AUR, not by this repository, so they are third-party even though Aria maintains both.
- **Removal is caught both ways:** computed from the golden files (anything gone from a set fails `make version-check` unless the major version rose) **and** declared — a removal also needs a *Removed* entry in the changelog, which the check reads.
- **Out of the promise**, as proposed: the daemon protocol (versioned and checked since items 149 and 152), the map's look and art, the TUI's layout, and the city's key bindings (their config keys are promised).

Ruled on 2026-10-20, through the roadmap manager, while slice 2 was planned:

- **The command line waits for [item 167](167-the-cli-has-spread-and-ships-no-man-pages.md)**, which analyses and consolidates it, with man pages, before 1.0 promises it; the command-tree golden file and the removal of `version` move there.
- **`status --json` promises a documented subset**: `id`, `pid`, `harness`, `title`, `state`, `cwd`, `branch`, `model`, `contextPercent`, `startedAt`, `lastActivity` and `prs`. The rest of the session model is still emitted, and listed as unpromised.
- **The frame and test flags** (`--screenshot`, `--keys`, `--hover`, `--record`, `--headless`, `--window`, `--script`) are hidden, unpromised, and built only into dev and debug builds — item 167's to do, with the command tree.
- **This slice's own removals go unchecked by the computed rule**, because v0.2.3 has no golden files to compare with; the *Removed* entries are written anyway, and the rule bites from the next release.

**The command tree waits for item 167** (Aria, 2026-10-20): she wants the commands and flags analysed and consolidated, with man pages, before 1.0 promises them, so the command-tree golden file and the removal of `version` follow [item 167](167-the-cli-has-spread-and-ships-no-man-pages.md); the other surfaces go ahead.
