# 250. A session whose turn ended over a running background command says it needs you

**Fixed 2026-10-26 (`b49c1a4`, r1061). Filed 2026-10-25 (r1032), found by item 246's session running the validation checklist's step 1 live. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`cd37e3f`, r1062).

Against installed 0.3.0, `claude agents --json --all` and `botropolis status --all --json`, matched by session id, agree except for one class: five background sessions (four item sessions and the performance manager) showed **needs you** while Claude Code's own session record said `"status": "shell"` and `claude agents` said working or blocked.
A record of `shell` is a session whose turn has ended while a background command it started is still running; it carries on by itself when that command finishes, so it does not need anyone.
`derive()` alone calls it working (`pkg/state`'s `TestRecordStatus`, "when the record says shell while the tail awaits the user"), but the daemon's Stop-hook overlay in `view()` (`botropolis/pkg/daemon/daemon.go`, near line 455) sets needs-you over it, because a Stop hook fired when the turn ended.
So the map raises a beacon, and `botropolis bar` changes colour, for sessions that are only waiting on their own command: the beacon that most needs to be right is wrong for every session that runs a long build in the background.

## The fix

The overlay yields to a `shell` record: a session whose record is `shell` is working, whatever its last Stop hook said, until the record changes.
Check the overlay's other inputs for the same shape while there, and say what was found.

Tests: in `pkg/daemon`, when a Stop hook fires for a session whose record says `shell`, it should not need you, and when the record then turns idle with the turn waiting, it should; and an acceptance case through the daemon with a session record staged as `shell`.

## Fixed

Each session now carries its record's status, and in `view()` an overlay that says only that the turn ended yields to a record of `shell`, so the session keeps the state `derive()` gave it — working, or unattended for an unattached background session — until the record changes.
The overlay is kept, so when the record turns idle the Stop still counts and the session needs you.

The overlay's other inputs, checked for the same shape:
a Notification of type `idle_prompt` is the same turn-ended signal and now yields to `shell` too;
a `permission_prompt`, or any other type, still needs you over `shell`, because a question asked is a question and the record can lag (agreed with the roadmap manager);
PreToolUse, PostToolUse and UserPromptSubmit set working, and SessionEnd sets resting, so none of them conflicts with `shell`.

Tests: `pkg/daemon`'s `TestDaemon` covers the Stop on a `shell` record and the record then turning idle, an unattached background session, and both notification types; `pkg/state` checks the record's status is carried.
`testing/acceptance/shell_test.go` runs botropolisd on a staged home and sends a real Stop through `botropolis-hook` to a `shell` session and to a `busy` control session; it waits for the control to show needs-you, so it cannot pass before the hook lands, and was red with the yield disabled.
The field is kept out of `status --json`, and the share veil keeps it as one of the CLI's own words (`cd37e3f`).
