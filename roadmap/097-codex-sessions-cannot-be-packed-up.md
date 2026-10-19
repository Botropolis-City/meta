# 97. Codex sessions cannot be packed up

**Fixed 2026-10-19 (`3ff79f6`, r778). Filed 2026-10-16 (r510) at Aria's request, from item 86. Nobody's call — the Claude side shows how.**

Item 86 added *pack up*, which takes a session off the map into the depot, and *unpack*.
A pack is recorded in the daemon's ledger, and only the Claude loader reads the ledger, so a Codex session (`pkg/harness/codex`) offers no *pack up* and a merged pull request never packs it.
Aria, 2026-10-16, chose to have this filed on its own rather than grow item 86.

The fix: the Codex loader reads the same ledger entries by session id and marks the snapshot's sessions packed, so the depot, the card's *pack up* and *unpack*, `Shift+P` and triage's `d` all work on Codex sessions as they do on Claude's.
A packed Codex session that does something new comes back by itself, as a Claude one does.

Tests: the loader cases item 86 wrote for Claude, data-driven over both harnesses.

## Closed

Packing already wrote any session's id to the ledger, since the card, `Shift+P` and triage's `d` all reach the Claude loader's `Pack`.
The fault was on the read side, and it was worse than filed: the Claude loader read a Codex id it had not shown as a Claude session whose transcript was gone,
so packing a Codex session left its building on the map and added a ghost crate with no conversation to the depot.

Each ledger entry now records the harness that showed it, empty for Claude's, so ledgers written before read the same, with no version bump.
The Claude loader brings back only its own gone sessions, and `harness.Multi` hands every other harness's sessions to the same ledger pass, so a pack, an unpack, coming back on new work and a demolish all hold for Codex.
It is done through `Multi` rather than in the Codex loader, as the fix above said, so that one loader stays the ledger's only writer and two in-memory copies cannot overwrite each other's saves (agreed with the manager, 2026-10-19).

Tests: `pkg/harness/ledger_test.go` runs item 86's loader cases data-driven over both harnesses through the real `Multi`, plus a demolished session staying off the map and each session showing exactly once.
Every Codex case was red before the fix,
and removing the harness filter, `Multi`'s pass or the field's `omitempty` each turns them red again.

**Not covered:** a merged pull request still cannot pack a Codex session, because the Codex loader reads no pull requests.
The same pass would pack it if Codex ever reports them.
