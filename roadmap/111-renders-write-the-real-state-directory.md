# 111. A headless render writes into the real state directory

**Open, in progress since 2026-10-18 in the session "item 111". Filed 2026-10-18 (r592) at Aria's request, from what item 109 found. Nobody's call — a defect.**

A headless or scripted run of `botropolis city` — the way item sessions render frames — reads and writes `~/.local/state/botropolis/`, the state of the person's own city, unless whoever starts it remembers to point `XDG_STATE_HOME` elsewhere.
On 2026-10-18 Aria's `layout.json` held 76 districts, 53 of them test directories from frames rendered by earlier item sessions (`/home/demo/src/*`, `/home/user/src/*`, `/src/*`, `/w/*`), each with a slot on her plan; since item 109 types every district the first time it is seen, those entries were being typed too.
They were removed by hand, with a backup kept beside the file.

## Where it comes from

Every store resolves its directory from `XDG_STATE_HOME` and falls back to the real one: `layout.go` in `botropolis/pkg/city`, `ledger.go` in `pkg/state`, `store.go` in `pkg/group` and `usage.go` in `pkg/claude`.
`botropolis-demo film` sets `XDG_STATE_HOME` to its own work directory (`pkg/demo/film.go`), so filmed demos are safe; a frame rendered directly with `--headless`, `--record` or `--script`, or a run with `--home`, is not.
Item 87 already refused to keep groups for a `--home` run, for the same reason.

## The fix

A run that is not the person's own city never touches their state: `--headless`, `--record`, `--script` and `--home` each imply a private state directory — a temporary one unless one is given — for every store at once, resolved in one place rather than four.

Tests: data-driven over those flags, a run should write nothing under the real state directory (with `HOME` and `XDG_STATE_HOME` pointed at a temporary directory the test owns), and an ordinary run should still use it; mutated red by removing the implication.

## Answered while building

- **The design** (manager, 2026-10-18): a `statedir` package resolves every store's directory in one place; `--headless`, `--record`, `--script` and `--home` make a private one after the headless re-exec and remove it on exit; a `--home` run is seeded with a copy of that home's own `.local/state/botropolis`, so a fixture home carries its own ledger, layout and groups without its files ever being written, which is also how a frame shows a session whose transcript is gone (item 109). No new flag or environment variable.
- **Probe and summary directories stay on the real default** (manager, 2026-10-18): they are where `claude -p` runs, fenced out of the city by path, not stores; a private run starts no probe or summary at all, with a test for it.
- **`--screenshot` alone stays an ordinary run** (manager, 2026-10-18): a picture of your own city keeps your own state, and it is the tests' control row.
