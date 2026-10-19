# 93. A heavy Codex history takes seconds to load at every daemon start

**Fixed 2026-10-19 (`c6d6306`, r679). Filed 2026-10-16 (r455) at Aria's request, from a measurement item 86 made.**

Depends on: nothing
Landed: slice 1 (`0b536c7`, r675).
Landed: slice 2 (`c6d6306`, r679).

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

## Measured

`BenchmarkLoadAHeavyHistory`, in botropolis's `testing/acceptance` so that the release's `make bench` tracks it, rebuilds item 86's history, since item 86's own rollouts were never kept: 2,000 rollouts of about 100 KB each, mostly tool output and reasoning.
On 14 cores the first load took **1.3 s** before this item, against item 86's 3.2 s on its own rollouts.

- **Slice 1, skipping lines before decoding them** (r675): **0.55–0.76 s**.
  Codex writes every line as `{"timestamp":T,"type":X,"payload":{"type":Y`, so the loader reads that header in place and decodes only the records it uses.
  A line of any other shape is decoded whole.
  The work counter "rollout lines decoded" holds the loader to exactly the lines used.
  A byte search for the record types across the whole line was tried first and was slower than decoding, because tool output is full of quotes.

- **Slice 2, decoding rollouts in parallel** (r679): **0.28–0.44 s**.
  It does no less work, so the benchmark is its only measure, and its tests hold the snapshot's order, its power, the cache's reuse and a skipped rollout under `-race`.
  On 14 cores it gains only about 2×, because what remains is mostly allocation and the collector rather than decoding.

The manager's rule (2026-10-19) was to build slice 2 only if the first load was still over about half a second after slice 1, which it was.
**Lever 3, show first and fill later, is not to be built**: it changes what the daemon's first snapshot means, and the cheaper levers are enough.

## Closed

Fixed in two slices, skipping lines before decoding them (`0b536c7`) and decoding rollouts in parallel (`c6d6306`), with the changelog line in `bf7d7c7`.
On the rebuilt benchmark the first load fell from 1.3 s to 0.28–0.44 s.
`TestDecodingOnlyWhatIsUsed` holds the decoding to exactly the lines used, and `TestLoadingManyRollouts` holds the parallel snapshot to the serial one.
**For Aria:** the 3.2 s baseline came from item 86's own synthetic rollouts, which were not kept, so the rebuilt history measured 1.3 s before this item on this machine; the two numbers are not one benchmark.
