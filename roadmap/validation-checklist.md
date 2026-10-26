# Validation checklist

The checks a release runs against a live city before it ships (`RELEASING.md` in botropolis).
Rewritten on 2026-10-25 by [item 246](246-the-validation-checklist-predates-0-3-0.md), against the city as it is after 0.3.0.
Every key and every word below is quoted from the app (`pkg/render/keys.go`, `pkg/city`, `pkg/ui`, the manual pages), not from memory.

The checklist used to be ten steps for Aria.
Most of them were things a script can do, so each step is now in one of three tiers:

- **Scripted**: a test checks it on every landing, and it needs no one.
- **Live**: a check against the real `claude` CLI on Aria's machine, which an agent runs and writes up below; it needs no desktop.
- **Aria's**: it needs her own terminal, notifications and desktop, so only she can run it.

## Before a run

1. Install the build under test from its package, and run `botropolis setup`, which registers the hooks, makes sure the daemon runs and prints the shell line.
   A city that meets an older daemon says so and offers **Restart Daemon**.
2. `botropolis doctor` checks the daemon, the hooks, a terminal, the claude CLI, the harnesses and the display; every line should pass.
3. `systemctl --user enable --now botropolis-notify` if the notifier is not running yet: it runs `botropolis notify`.
4. Make any session the steps create or demolish in a scratch folder, such as `~/workspaces/botropolis-validation/valley`, so nothing real is touched.

## Scripted

These run in `make test`, so `make land` runs them on every landing.
A step here fails a landing, rather than waiting for someone to try it.

| # | check | tests |
| --- | --- | --- |
| S1 | `enter` on the selection attaches it, and on a resting session resumes it in its own folder first; `botropolis attach <id>` does the same in the terminal you are in | `pkg/control` `TestControl` ("it should spawn a terminal running claude attach"), `pkg/commands` `TestSessionsOpen`, `testing/acceptance` `TestAnswerAndComeBack` |
| S2 | `c` starts a session in the selected building's folder or the hovered district's, `shift+n` opens New session for any folder, and `botropolis new` prints the job id | `pkg/city` `TestSelectionActions`, `pkg/render` `TestNewSession`, `testing/acceptance` `TestStartASessionAnywhere`, `pkg/cli` `TestSessionCLIs` |
| S3 | when the city regains focus after something needed you, it opens "While you were away" listing it, and otherwise opens nothing | `testing/acceptance` `TestTheAwayListOnRefocus` (item 246) |
| S4 | `x`, or a click on the plant: the breakdown's 24 h cost is the strip's, and a row none of whose messages has a price says "cost unknown", never "$0.00" | `pkg/city` `TestBreakdown` ("it should give the strip the 24 h breakdown's own cost"), `pkg/ui` `TestLayoutBreakdown` (item 246) |
| S5 | `b`, `t`, `s`, `?`, `x`, `g`, `/`, `w`, `shift+w`, `v`, `shift+n`, `shift+q`, `m`, `h`, `o` and `i` each open their panel, and `esc` closes it, leaving nothing else open and the camera where it was (`w` leaves the session it stopped on selected) | `testing/acceptance` `TestEveryPanelClosesOnEscape` (item 246); it fails as [item 137](137-escape-skips-the-sidebar-and-the-hidden-interface.md) did when a rung of the ladder is removed |
| S6 | `d d` on the selection: "press d again within 3s to demolish <title>", then "demolished <title>"; it leaves the map, and stays gone after the daemon restarts | `pkg/city` `TestDemolish`, `pkg/commands` `TestDemolished`, `pkg/daemon` `TestServeForget`, `pkg/state` `TestLedgerForget` ([items 144](144-a-demolished-session-stays-on-the-map.md) and [145](145-a-demolished-session-with-a-transcript-comes-back.md)) |
| S7 | `botropolis bar` gives waybar the class `needs-you` and a tooltip of "needs you:" with each title, longest-waiting first | `pkg/commands` `TestBar`, `pkg/cli` `TestBarCLI` |
| S8 | `b` with more rows than fit: the wheel, `pgup`, `pgdn`, `home` and `end` scroll it, "N more above" and "N more below" say what is out of view, and `tab` keeps the selected row in view | `testing/acceptance` `TestSidebarScrolls`, `pkg/ui` `TestLayoutSidebar` ([item 136](136-the-sidebar-cuts-off-rows-past-the-window.md)) |
| S9 | a session the CLI calls `shell`, as `!` or a background command makes it, reads as working, not needs-you, even after its Stop hook; a permission prompt still needs you | `pkg/state` `TestRecordStatus` ("when the record says shell while the tail awaits the user"; [bug 12](012-a-third-cli-status-word-appeared.md)), `pkg/daemon` `TestDaemon` ("when a Stop event arrives for a session whose record says shell"), `testing/acceptance` `TestShellRecord` ([item 250](250-a-session-running-a-background-command-says-it-needs-you.md)) |
| S10 | a state change reaches the daemon's snapshot promptly while the statistics backfill runs | `pkg/daemon` `TestStateChangeDuringBackfill` ([item 138](138-state-changes-lag-while-statistics-backfill.md)) |

What these do not cover is what the next two tiers are for:
the tests use a fake `claude` and a fake terminal, and stage demo homes rather than a real one.

## Live

| # | check | last run |
| --- | --- | --- |
| L1 | `botropolis status --all --json` against `claude agents --json --all` and the CLI's own records in `~/.claude/sessions`, read in the same pass and matched by `sessionId`: each live session's state agrees | 2026-10-25, below: one class disagreed, fixed by [item 250](250-a-session-running-a-background-command-says-it-needs-you.md) at r1061; run it again against the next release |
| L2 | `botropolis rm <id>` on a stopped session in the scratch folder: it leaves `claude agents --json --all` and the daemon within seconds, and stays off after `systemctl --user restart botropolisd` | 0.2.2, 2026-10-19, below: passes |

## Aria's

Each of these needs a real window, a real terminal or a real notification.
Run them against the release build, in order; each says what to press and what to see.

| # | press | see |
| --- | --- | --- |
| A1 | `botropolis`; `tab` to the first session that needs you, then `enter` | your terminal opens running `claude attach` on that conversation. Close the window: the session keeps running, and its building stays on the map. |
| A2 | hover the scratch folder's district, press `c` | the status line says "new session in <dir>", and a new building rises in that district within seconds |
| A3 | with the notifier running, prompt a session in the scratch folder, switch the city's window away before it answers, and wait | a desktop notification "<title> needs you", its body the folder and branch. Switch back: "While you were away" lists it, "needs you". |
| A4 | in a session attached in your terminal, type `! sleep 20`, then look at the map | its building reads as working while the command runs, not needs-you |
| A5 | waybar with the module in the README (`botropolis bar --watch`), while a session needs you | the module takes the `needs-you` class and your style for it, and its tooltip names the session |
| A6 | `botropolis status --live` in a terminal; `enter` on a resting session; `x` then `x` again on one in the scratch folder | `enter` resumes it and attaches; the first `x` says "press x again within 3s to demolish <title>", and the second removes it |

S3, A3's second half, is scripted, but only through a stand-in for the window's focus; A3 is the check that the real window manager's focus reaches it.
Likewise S9 stages the `shell` record; A4 is the check that a real `!` in Claude Code writes it.

## Step L1, run 2026-10-25

Against the installed 0.3.0 package, with 44 records in `claude agents --json --all` and 237 sessions in `botropolis status --all --json`.

**Agrees.** Every session the CLI calls `working` whose record says `busy` is `working` in botropolis, every `done`, `stopped` and `failed` job with no live process is `resting`, and every idle background session that has handed its turn back is needs-you, where the CLI says `done`, which is the CLI's word for a finished turn rather than a disagreement.

**One class disagreed, filed as [item 250](250-a-session-running-a-background-command-says-it-needs-you.md) and fixed at r1061.**
Five background sessions whose record says `shell`, where the CLI calls them `working` or `blocked`, showed as needs-you: each had ended its turn while a background command was still running.
`derive` alone called `shell` working; the daemon's overlay from the Stop hook was newer and set needs-you over it.
Item 250 made the overlay yield to a `shell` record, and S9 now covers the daemon's path as well as the derived state.

Two jobs the CLI still calls `blocked` have no live process, and botropolis calls them resting, which is right: nothing is running to answer.
One the CLI called `blocked` while its own record said `busy` was working in botropolis; that is the CLI disagreeing with itself between two reads, not botropolis.

**Two jobs are not shown, by design.**
`claude agents --all` lists two `done` background jobs with no transcript and no session record anywhere under `~/.claude`, so there is nothing to draw, read or resume, and `claude rm` is the only way to remove them.

## History

The ten steps as written on 2026-09-29, against r293, and every run of them, kept as they were run.
The table is the old checklist's own; its words — parked containers, `parked_days` — are the city of that date.

Ten steps, written for Aria to run against a live city.
It lived inside item 67's file until 2026-09-29 and was cross-referenced by a section number that no longer existed, which is why it had never been run end to end.

**Preconditions.** Install the latest build, restart the daemon, enable notify.
As of 2026-09-29 the installed package is `r293.f920abc` against a HEAD of r320, so the steps below have been run against a build seven-and-twenty revisions old; everything since is documentation and tooling, so no behaviour differs, but a real run should install first.
I have not installed or restarted anything on Aria's machine for this.

| # | step | state |
| --- | --- | --- |
| 1 | `botropolis status` — every live session's state matches what you know it is doing | **run 2026-09-29**, see below |
| 2 | `botropolis`, Tab to the first needs-you, Enter: terminator opens with `claude attach`, Ctrl-Z leaves it running | needs Aria |
| 3 | `c` on a district: a new background session in that folder, on the map within seconds | needs Aria |
| 4 | let a session hand back while the map is unfocused: notification fires, away panel shows it on refocus | needs Aria |
| 5 | `x` on the plant: the breakdown's 24 h cost is within a few dollars of the strip, and no row says `$0.00` for millions of tokens | needs Aria's eye; the map is running |
| 6 | `b`, `t`, `s`, `?`, `h`, `r`, `n`, `/` — each opens, closes with Escape, none leaves the map wrong | needs Aria |
| 7 | `d d` on a parked container: gone from the map and from `claude agents --json --all` | needs Aria |
| 8 | `botropolis bar` in waybar: the class changes colour when a session needs you | **run 2026-09-29, passes** |
| 9 | `b` with more projects than fit: the wheel over the sidebar and PageUp, PageDown, Home and End scroll it, "N more above" and "N more below" say what is out of view, the arrows still pan, and `tab` keeps the selected session's row in view | needs Aria |
| 10 | type `!` in a session, then look at the map: it reads as working, not needs-you (bug 12) | needs Aria |

Old step 1 is L1, 2 is S1 and A1, 3 is S2 and A2, 4 is S3 and A3, 5 is S4, 6 is S5, 7 is S6 and L2, 8 is S7 and A5, 9 is S8, and 10 is S9 and A4.

## Step 1, run 2026-09-29

Compared against `claude agents --json --all` (41 records: 17 `done`, 13 `blocked`, 8 `stopped`, 2 `working`, 1 with no `state` key at all).

**Correct and confirmed.** The row whose title is `f26cfe27` is right: that is the CLI's *own* `name` for an untitled session, so bug 15's truncation is working rather than bug 2 recurring. Three sessions the CLI calls `blocked` are absent because they are idle 7.9, 8.2 and 10.7 days against `parked_days` of 7 — correctly excluded, not missing.

**One defect filed and withdrawn the same day.** [Item 71](071-two-live-sessions-missing-from-status.md) reported two live sessions missing; they were present under titles the CLI does not use, and the filing had reconciled on a non-key column. It is kept because it is what produced `status --json`.

**Re-run by id after r322 added `status --json`, and step 1 passes.**
`claude agents` reports 14 sessions as blocked or working. Matched by `sessionId` against `botropolis status --all --json`: **ten are present with the state that maps correctly**, and the other four are idle 7.9, 8.3, 8.3 and 10.7 days against `parked_days` of 7, so they are not catalogued — correct. Three more resolve as `parked` where the CLI still says `blocked`, which is the same aging and also correct.
Nothing is missing and nothing disagrees.

**The finding that mattered was about this step rather than the program, and it is fixed.** `botropolis status` printed no session id and had no `--json`, so its rows could only be matched to `claude agents` by title — and titles are not unique. That is why this step sat unvalidated for so long, and it is why the first attempt at running it produced a false positive. `status --json` (r322) emits `state.Session` as modelled, so the reconciliation is by id and step 1 is now a check that either passes or names the session that failed.

## Step 8, run 2026-09-29, passes

`botropolis bar` emits waybar JSON with `"class":"needs-you"` and a tooltip naming each one, so the class does change with state.

**Sampled simultaneously with `botropolis status`** rather than minutes apart, because the first comparison appeared to show `bar` calling two sessions needs-you that `status` called working — which was two samples of a changing state, not a disagreement. Taken in the same instant, the two agree exactly: 11 needs-you each, none in one and not the other.

## Steps 2-10, a dry run before 0.2.0, 2026-10-19

Run by the roadmap manager overnight, at Aria's request, against a build of main (r704) rather than the release, to find what 0.2.0 should fix before it is cut; the run against the release itself follows.
Nothing was installed: the binaries ran from a scratch folder, beside a scratch daemon with its own socket, state directory and a copy of the config, on Aria's display, with every key pressed by the city's own `--keys` and `--script` cues rather than injected into the desktop.
Sessions were made for it in a scratch folder (`~/workspaces/botropolis-validation/valley`), so attach, new, demolish and `!` touched only those.

| # | result |
| --- | --- |
| 2 | **passes**: the selected needs-you session's Enter opened terminator running `claude attach`; ending the client left the session running |
| 3 | **passes**: `c` started a background session in that folder, and the stream said `started` |
| 4 | not run yet |
| 5 | not run yet: item 116 is rewriting the breakdown's cost, so it is run against the release |
| 6 | **two fail**: Escape leaves the sidebar open and opens settings on top, and with the interface hidden it opens settings invisibly ([item 137](137-escape-skips-the-sidebar-and-the-hidden-interface.md)); the rest close or are one-shot |
| 7 | **passes** by its own path: `botropolis rm` on a stopped session removed it from `claude agents --all` and from the daemon within 3 s; `d d` itself could not be scripted, because its 3 s arming is wall-clock and a hidden window records a frame every ~14 s |
| 8 | **passes**: `bar` gives class `needs-you` and names each one |
| 9 | **fails**: the sidebar cuts off every row past the window's bottom, with no scroll ([item 136](136-the-sidebar-cuts-off-rows-past-the-window.md)) |
| 10 | **passes** once settled (0.15-1.1 s), but **6-15 s late** while the first-run statistics backfill runs ([item 138](138-state-changes-lag-while-statistics-backfill.md)) |

Also seen: a district named "." and two districts named botropolis ([item 139](139-districts-named-dot-and-twins.md)).

## Steps 2-10 against the 0.2.0 release, 2026-10-19

The released `botropolis-0.2.0-linux-amd64.tar.gz`, unpacked into a scratch folder and run the same way as the dry run above: a scratch daemon on a fresh state directory (as an upgrade from 0.1.7 starts), Aria's display, the city's own key cues, and sessions in `~/workspaces/botropolis-validation/valley`. The machine was loaded (average 15-20) by a demo film and a package build running beside it.

| # | result |
| --- | --- |
| 2 | **passes**: Enter on the selected needs-you session opened `claude attach` in terminator |
| 3 | **passes**: `c` started a background session in that folder |
| 4 | **passes** for the notification: `botropolis notify` sent "val needs-you needs you" over D-Bus when the session handed back; the map's away panel on refocus cannot be shown from a locked screen and is unchecked |
| 5 | **passes**: the plant's 24 h figure ($428.94 at API list prices, 5,377 messages) is the strip's, and no row prices millions of tokens at $0.00 |
| 6 | **passes**: Escape now closes the sidebar and brings the hidden interface back (item 137) |
| 7 | **fails**: a removed session leaves `claude agents --all` but stays on the map as ruins, because the ledger never forgets it ([item 144](144-a-demolished-session-stays-on-the-map.md)) |
| 8 | **passes**: `bar` gives class `needs-you` and names each one |
| 9 | **passes**: PageDown scrolls the sidebar with "N more above / below" (item 136) |
| 10 | **passes** during the first-run backfill: 1.2 s once, then 0.23 s (item 138) |

Also found: the daemon can miss its 10 s start deadline on a large, busy home and exit — 3 of 6 fresh starts tonight ([item 143](143-the-daemon-can-miss-its-start-deadline.md)). Items 143 and 144 make 0.2.1.

**Step 7 again, on 0.2.2 and 0.2.1.** 0.2.1 (item 144) still left a removed session on the map when it had a conversation, because `claude rm` keeps the transcript ([item 145](145-a-demolished-session-with-a-transcript-comes-back.md)). On the 0.2.2 release a prompted session, stopped and removed, left the daemon within 3 s with its transcript still on disk, and stayed off after a daemon restart: **step 7 passes**. 0.2.1's start fix held 6 of 6 fresh starts under the same load.
