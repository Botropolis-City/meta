# 145. A demolished session whose transcript remains still stands on the map

**Open, in progress since 2026-10-19 in the session "item 145". Filed 2026-10-19 (r743), from validating the 0.2.1 release binaries. Nobody's call — a defect.**

Depends on: nothing

[Item 144](144-a-demolished-session-stays-on-the-map.md) made demolishing forget a session from the daemon's ledger.
Checked against the 0.2.1 release: a background session that had answered one prompt, stopped and then removed (`botropolis rm`, the path `d d` takes), left `claude agents --all` and the ledger's job, but still stood on the map as **resting**.
`claude rm` deletes the background job, not the conversation: the session's transcript stays in `~/.claude/projects/`, and the loader builds a resting session from any transcript it finds, so forgetting the ledger entry changes nothing for it.
Item 144's own test passed because the session it was found with had never been prompted and had no transcript. The roadmap manager ruled out a tombstone in 144 on the belief that the transcript was gone at once; that was wrong for any session with a conversation.

## The fix

Demolishing records the session as demolished (a tombstone in the ledger, written by the daemon or noted for it as item 144 does), and the loader leaves a demolished session off the map and out of `status` whatever transcripts remain; its statistics are untouched, as item 144 kept them.
Botropolis does not delete the transcript itself: the conversation is Claude Code's file.
Re-check what the card's demolish text promises (`pkg/city/actiontext.go`, "Its conversation is gone for good") against what `claude rm` does, and make it say what happens.

Tests: a session with a transcript, demolished → it should not be in the next load or the snapshot; a demolished session's transcript still on disk → it should stay off after a daemon restart; a session Claude Code cleaned up on its own → unchanged (item 86); the card's text should match.
