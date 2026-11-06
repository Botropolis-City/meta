# 346. A session that pauses for a second or two mid-work flips to needing you

**Open, in progress since 2026-11-06 in the session "item 346". Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — she has said what it should do.**

Aria: *"we need a debounce for idle. If a session is running and stops for a second or two and continues, it should stay showing active not idle"*.

## Where it stands

There is no debounce anywhere between a session's signals and what the city shows.

- A Stop hook sets the overlay to `NeedsYou` at once, and `Apply` notifies subscribers in the same call (`pkg/daemon/daemon.go`).
- `derive` in `pkg/state/state.go` gives `NeedsYou` the moment the record says idle or the transcript's tail hands the turn back.
- `botropolis notify` sends a desktop notification on any change into `NeedsYou` (`Notify.Offer` in `pkg/commands/notify.go`), so a pause can also cost a notification.
- The event log gets its `needs-you` line the same way, so the Stream and the journal repeat it.

## The evidence so far

Not reproduced on demand.
Sampling `botropolis status --json` every half second for 75 seconds, across 7 live sessions, saw no change of state at all, so this needs catching while a session is doing the pausing.
`botropolis events` lists 125 `needs-you` lines in its last 300, but says nothing about how long each one lasted, so that count is not a measure of this.
The first slice should be a reproduction: a fake session that ends a turn and starts another within a second.

## The fix

A session going from working to idle shows working for a hold of about three seconds, a little over Aria's "a second or two", and shows idle only if nothing new has happened by then.
It belongs in the daemon, upstream of the snapshot, so the map, `status`, `bar`, `notify` and the event log all agree.
A hold on the map alone would still send the notification.

**The hold applies only to going idle.**
These show at once, because a delay there is the defect that matters more:

- a permission prompt or a question: `StatusWaiting`, `TurnNeedsInput`, or a `Notification` hook other than the idle prompt (item 331);
- a session ending, or resting;
- a session starting work again, which also cancels the hold.

The daemon's `releaseClock` can be faked, which the tests below need; `scheduleRelease` beside it coalesces rescans and is not this.
The hold's length should be one constant, and whether it needs to be a setting can wait until someone asks.

## Tests

With a fake clock, in `pkg/daemon`:

- when a working session goes idle, it should still show working inside the hold;
- when the hold passes with nothing new, it should show needing you;
- when it works again inside the hold, it should never have shown needing you, and it should log no `needs-you` event;
- when it hits a permission prompt, it should show needing you at once;
- when it ends, it should rest at once.

In `pkg/commands`, a pause inside the hold should send no notification.

## Answered while building

- **The test tree** (roadmap manager, 2026-11-06): approved as sent — the hold in `pkg/daemon` on a fake `releaseClock`, covering the item's five cases plus a record turning idle on a rescan, a session that was never working needing you at once, and `notify` sending nothing inside the hold and one notification after it.
- **The reproduction** (roadmap manager, 2026-11-06): the first red test — a Stop then a PreToolUse within a second, asserting no `NeedsYou` was ever shown — is the reproduction the item asked for; no separate acceptance test.
- **What the held session shows** (roadmap manager, 2026-11-06): its last state, tool and subject, so the bench does not flicker; it follows from "shows working for a hold".
- Lands as one slice, with the changelog entry and a line in `design/session-lifecycle.md`.
