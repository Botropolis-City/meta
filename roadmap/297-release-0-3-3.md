# 297. Release 0.3.3

**Open, in progress since 2026-10-27 in the session "item 297". Filed 2026-10-27 (r1153) at Aria's request. Nobody's call — Aria set what it holds and what it runs.**

Depends on: 280 (slice 3), 286, 290, 293 (slice 1), 212 (slice 21), 298

Aria, 2026-10-26, on 0.3.2's plan: everything planned for 0.3.2 goes into 0.3.3, which runs what 0.3.2 waived (*"Run everything. We already skipped re-film for 0.3.1"*).
And 2026-10-27, on what it waits for: *"Ship with just window close"*, item 293's first slice, the tray following later; then *"That path looks good. Let's go"*.

## What it holds

Everything on `main` once items 280 (City Hall and the clinic), 286 (claude actions off the loop), 290 (paste) and 293's first slice (catching the close request) have landed, and item 212's still key has been measured: kept if a quiet pair puts fit below r1120's in the same sitting, its slice 2 reverted otherwise.
Item 270's last bar and the other ready items do not hold it.

## Steps, from `botropolis/RELEASING.md`, nothing waived

1. Merge `[Unreleased]`'s several `### Fixed` (and other) headings, left by parallel landings, into one of each, and make every entry read for the user; `VERSION` to 0.3.3, `[0.3.3] - <date>`; `make version-check`; `make land`; CI green.
2. **Landings hold** from the bump until the tag.
3. The performance manager's `make test-performance` at the bump's commit.
4. **The soak**, the first real one: item 245's runner on that commit's build, `IPV4=1` while this machine has no IPv6, the box booking its own cancellation and uploading to item 266's bucket; Aria types the price; within the growth budget, or 0.3.3 waits on the fix.
5. **The validation checklist**: the agent's live steps, and Aria's A1 to A6, against that build.
6. **The re-film**: `make demo-media` and `make media-import`, with item 76's new media; Aria judges the frames.
7. The release workflow, `dry_run` first, then for real; the AUR packages with `aur-update`; the website rebuilt (by hand unless `SITE_DISPATCH_TOKEN` is stored, item 267).

## Answered while building

- **The bump and the release check** (manager, 2026-10-27): the bump landed as `7c852c5` (r1178) on item 270's slice 4; the release check failed item 270's 600-district fit bar, five quiet runs of five at 16.05–17.72 ms against 16, the first time `main` was measured against it, and a control at `c616baf` passed, placing the cost in r1166–r1176. Item 280's clinic was walking every building per frame to count; its fix, `77ae413` (r1179), passes five quiet runs at 15.24–15.93 ms and the full suite with every budget met, so 0.3.3 is cut from `77ae413`. The fit bar's margin is under a tenth of a millisecond, to carry into 0.3.4. A suspected creep in the 2,000-session daemon's memory was within run-to-run spread over ten quiet runs. The soak waits for Aria's 1Password approval in the morning.
- **The re-film** (Aria, 2026-10-27): 46 shots filmed overnight from `77ae413`, passed, *"publish with 0.3.3"*: the site imports them with the release. **The soak**: the first box (3100496) was cancelled when one scp timed out after its set-up, nothing soaked, about EUR 0.18 (item 301); reordered as 3100616 under Aria's OK.
- **The checklist** (Aria, 2026-10-27, on the candidate `77ae413` installed from CI's Arch package): A1 to A6 pass. The scratch folder step 4 named did not exist, and the checklist now says how to make it. Her notes on `c` became item 302, for 0.3.4.
