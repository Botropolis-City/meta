# 248. A synthetic history of real size can only be made inside `go test`

**Done 2026-10-25 (`5726e7b`, r1044). Filed 2026-10-25 (r1031), from item 245. Nobody's call — a tool the soak needs.**

Depends on: nothing

[Item 245](245-test-machines-in-the-cloud.md)'s overnight soak runs on a rented machine, which must never get a copy of Aria's own history, so it stages a synthetic history the size of hers instead: at least 200 sessions in 150 projects.
botropolis already generates such homes for its cost tests (`ManySessions` in `botropolis/testing/helpers/history.go`, with the home built beside it), but the generator takes a `testing.TB`, so nothing outside `go test` can drive it.

## The fix

Move the generator's core out of the test helpers into a package a binary can import (under `pkg/demo`), keeping `testing/helpers` as thin wrappers so every cost test's fixture is byte-for-byte what it was, and add `botropolis-demo synth-home --home DIR --sessions N --projects M --seed S`.
It writes only under `--home`, refuses a directory inside the user's real `~/.claude` or `$HOME/.claude`, and prints the counts it wrote.

Tests: the same seed writes the same home; the counts asked for are the counts written; the cost tests' fixtures are unchanged (a hash of a seeded home before and after the move); a `--home` inside the real `~/.claude` is refused and nothing is written; the home loads in the daemon as that many sessions in that many projects.

## Answered while building

The manager approved these on 2026-10-25:

- **An exact project count.** `ManySessions` draws its directories at random, so not every one is used.
  `SynthHistory` gives the first M sessions one project each and draws the rest, so `--projects 150` writes 150.
  `ManySessions` keeps its own draws, so the cost tests' homes do not change.
- **No second history.** `synth-home` refuses a `--home` that already has a `.claude`, since a second run would be added to `history.jsonl`.
  It also refuses one whose `.claude` would resolve, with links followed, inside `~/.claude`, `$HOME/.claude` or `$CLAUDE_CONFIG_DIR`, so `--home=$HOME` is refused too.
- **`--end` defaults to now**, so the soak's history falls in the last 30 days, and the tests pin it.
- **"Loads in the daemon" means `state.Load`**, the daemon's own loader.

## Closed

The generator moved to `pkg/demo/synthhome.go`, with `testing/helpers` kept as aliases and one-line wrappers.
The three cost tests' copies of the home-writing loop became `Home.WriteHistory`.
`testing/helpers/history_test.go` hashes the cost tests' three seeded homes.
Its hashes were recorded in their own commit before the move (`de3b93c`, r1043), and they still match after it.
A one-byte mutation of the writer turned all three red.
`cmd/botropolis-demo/synthhome_test.go` writes 200 sessions in 150 projects and loads them through `state.Load` as 200 sessions in 150 working directories.
It also checks that the same seed writes the same files, and that a home with a `.claude`, or `$HOME` itself, is refused with nothing written.
Removing the refusal or the every-project rule turned those tests red.

Usage: `botropolis-demo synth-home --home DIR --sessions 200 --projects 150 --seed 248`, which prints `wrote 200 sessions in 150 projects, N prompts, to DIR/.claude`.
Item 245's `run-soak --history DIR` can take its output as it is.
