# 93. A heavy Codex history takes seconds to load at every daemon start

**Open. Filed 2026-10-16 (r455) at Aria's request, from a measurement item 86 made. Nobody's call — the cost is accepted for now and the levers are known.**

Item 86 stopped taking old sessions off the map, so the Codex loader now reads every rollout there is.
Measured on a synthetic history: 2,000 rollouts of about 100 KB took 3.2 s to load the first time; 400 rollouts of 1 MB took 0.75 s once item 86 gave Codex the 64 KB head-and-tail window Claude's catalogue reads (`c3223ba`), against 4.4 s read whole.
Reloads after that take milliseconds.
Aria accepted the first load as it stands on 2026-10-16 and asked for decoding lazily to be filed on its own.

## Where the time goes

`Loader.Load` in `pkg/harness/codex/codex.go` stats every rollout and calls `readRollout` for any whose size or modification time is not in `l.cache`.
That cache is in memory, so **every daemon start** is a first load, not only the first ever.
The window bounds the bytes per rollout; what remains is `session.apply` running `json.Unmarshal` on every line read, most of which it then ignores.

## Levers, cheapest first

- Skip lines before decoding them: check the record's type with a byte search and unmarshal only the kinds `apply` uses.
- Decode in parallel across rollouts: they are independent, and the loop is one goroutine.
- Show first, fill later: put every session on the map from its first line, which carries its id and directory, and decode the rest in the background, oldest last.

A cache written to disk would make every start after the first fast, but it is a copy derived from another tool's data, which the project avoids; it is listed here so that it is not reached for first.

The benchmark item 86 recorded is the measure: re-run it, and record the number beside 3.2 s.
