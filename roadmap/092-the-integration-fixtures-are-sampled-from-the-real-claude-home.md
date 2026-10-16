# 92. The integration fixtures are sampled from the real Claude home, so the tests depend on whatever it holds

**Open. Filed 2026-10-16 (r445) at Aria's request, from a failure item 87 hit. Nobody's call — a defect.**

`make test-integration` and `make test-acceptance` both depend on `fixtures`, which runs `tools/make-fixtures.py` to copy a scrubbed slice of the real `~/.claude` into `testing/helpers/fixtures/sample/`.
That directory is git-ignored, so every run tests against whatever this machine's Claude Code last wrote.
The testing rules say tests rely on no outside state; these rely on all of it.

## How it showed

Item 87 found `testing/integration/claude`'s `TestReadTranscriptFromFixture` failing on this machine.
The newest transcript the script sampled (`1fcf29d8…`) held only an `ai-title` and an `agent-name` record — no directory and no prompt — and the test rightly expects a directory in every conversation that is not a bridge stub.
Item 82's `04186ff` taught the script to leave such transcripts out.
That fixed the symptom: the next shape Claude Code writes that the script's selection does not expect will turn the suite red again, on one machine and not another.

## The other half: where there is no Claude home, nothing runs

`helpers.FixtureHome` (`testing/helpers/fixtures.go:26`) calls `t.Skipf` when the fixture has not been generated.
CI has no `~/.claude`, so every test built on the fixture skips there and the run reads green.
A skipped test that reads like a passing one is the silent fallback `CLAUDE.md` warns about: the guard fails where its inputs come from.

## The fix

A checked-in synthetic fixture: a small Claude home written by hand, never sampled from a real one, holding each shape the readers must handle — a conversation, a bridge stub, a session with subagents, a road between two repositories, and the title-only transcript that broke this.
`fixtures` keeps its job as a tool for sampling new shapes from a real home, and stops being a dependency of the test targets.
`FixtureHome` then fails, not skips, when the fixture is missing, because a checked-in fixture is never legitimately absent.

What it touches: the `Makefile`'s `test-integration` and `test-acceptance` lines, `.gitignore`'s `testing/helpers/fixtures/` line, `testing/helpers/fixtures.go`, and every test that reads `sample` — which must then hold on the synthetic home, including the manifest the tests read.
`make gif` records from the same fixture, and item 76 owns the website's media, so the GIF moving to a synthetic home is that item's to judge.
Nothing sampled from a real Claude home is committed: `make publishable` reviews images, not fixtures, so the hand-written home is read before it is committed.
