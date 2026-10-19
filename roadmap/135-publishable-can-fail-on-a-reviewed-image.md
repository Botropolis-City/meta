# 135. make publishable can fail on an image that is on the reviewed list

**Fixed 2026-10-19 (`ac84348`, r688). Filed 2026-10-19 (r685), from item 99. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`ac84348`, r688).
Landed: slice 2 (`33e2432`, r689).

`botropolis/tools/check-publishable` failed once saying `docs/screenshots/r460-item-87-new-session.png` "is not on the reviewed list" though it is, then passed three times in a row (item 99, 2026-10-19).
The script runs under `set -o pipefail`, and line 251 reads `printf '%s\n' "${reviewed}" | grep -qxF "${img}"`: `grep -q` exits on its first match, and if `printf` is still writing it dies of SIGPIPE, so the pipeline fails although grep matched.
The longer the reviewed list and the earlier the image sits in it, the likelier it is; a guard that fails for nothing teaches everyone to rerun rather than read.

## The fix

Match without a pipe — `grep -qxF -- "${img}" <<<"${reviewed}"`, or an associative array built once — and look for the same `printf | grep -q` shape elsewhere in `botropolis/tools/` and in the meta repository's `tools/`.

Tests: an acceptance case that runs the check with a reviewed list long enough to make the race near-certain (tens of thousands of lines, the image first) and expects it to pass every time over many runs; red before the fix.

## Closed

`tools/check-publishable` matches each image with `grep -qxF -- "${img}" <<< "${reviewed}"` (`ac84348`, r688).
`testing/acceptance/publishable_test.go` copies the script into a temporary repository with its own bare `github` remote, pads the reviewed list to 50,001 lines with the image first, and runs it 20 times.
With the pipe put back it fails every run, and with the fix it passes every run.

The same shape elsewhere landed as slice 2 (`33e2432`, r689).
The meta repository's `tools/` already used here-strings.
In botropolis, `check-version`, `check-packages`, `fetch-kits` and `measure-render` no longer pipe into a reader that exits early.
`TestCheckPackagesLicences` covers the two `check-packages` sites and fails with either one mutated, and `make lint` runs `check-version`.
`fetch-kits` was checked by hand, since it needs the network, and `measure-render` has no test.

Flagged for Aria: two of those sites were worse than a flake.
`fetch-kits:40` and `check-version:47` assigned the pipeline under `set -e`, so a grep with no match ended the script with exit 1 and no output.
Their "no download link" and "no released version heading found" messages could never print, and now they do.
