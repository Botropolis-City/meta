# 97. Codex sessions cannot be packed up

**Open. Filed 2026-10-16 (r510) at Aria's request, from item 86. Nobody's call — the Claude side shows how.**

Item 86 added *pack up*, which takes a session off the map into the depot, and *unpack*.
A pack is recorded in the daemon's ledger, and only the Claude loader reads the ledger, so a Codex session (`pkg/harness/codex`) offers no *pack up* and a merged pull request never packs it.
Aria, 2026-10-16, chose to have this filed on its own rather than grow item 86.

The fix: the Codex loader reads the same ledger entries by session id and marks the snapshot's sessions packed, so the depot, the card's *pack up* and *unpack*, `Shift+P` and triage's `d` all work on Codex sessions as they do on Claude's.
A packed Codex session that does something new comes back by itself, as a Claude one does.

Tests: the loader cases item 86 wrote for Claude, data-driven over both harnesses.
