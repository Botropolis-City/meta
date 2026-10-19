# Validation checklist

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
| 9 | `b` with more projects than fit: the sidebar scrolls and the cursor row stays visible | needs Aria |
| 10 | type `!` in a session, then look at the map: it reads as working, not needs-you (bug 12) | needs Aria |

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
