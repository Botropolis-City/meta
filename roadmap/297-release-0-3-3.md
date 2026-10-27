# 297. Release 0.3.3

**Open. Filed 2026-10-27 (r1153) at Aria's request. Nobody's call — Aria set what it holds and what it runs.**

Depends on: 280, 286, 290, 293 (slice 1), 212

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
