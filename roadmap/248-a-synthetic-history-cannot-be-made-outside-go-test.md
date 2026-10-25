# 248. A synthetic history of real size can only be made inside `go test`

**Open, in progress since 2026-10-25 in the session "item 248". Filed 2026-10-25 (r1031), from item 245. Nobody's call — a tool the soak needs.**

Depends on: nothing

[Item 245](245-test-machines-in-the-cloud.md)'s overnight soak runs on a rented machine, which must never get a copy of Aria's own history, so it stages a synthetic history the size of hers instead: at least 200 sessions in 150 projects.
botropolis already generates such homes for its cost tests (`ManySessions` in `botropolis/testing/helpers/history.go`, with the home built beside it), but the generator takes a `testing.TB`, so nothing outside `go test` can drive it.

## The fix

Move the generator's core out of the test helpers into a package a binary can import (under `pkg/demo`), keeping `testing/helpers` as thin wrappers so every cost test's fixture is byte-for-byte what it was, and add `botropolis-demo synth-home --home DIR --sessions N --projects M --seed S`.
It writes only under `--home`, refuses a directory inside the user's real `~/.claude` or `$HOME/.claude`, and prints the counts it wrote.

Tests: the same seed writes the same home; the counts asked for are the counts written; the cost tests' fixtures are unchanged (a hash of a seeded home before and after the move); a `--home` inside the real `~/.claude` is refused and nothing is written; the home loads in the daemon as that many sessions in that many projects.
