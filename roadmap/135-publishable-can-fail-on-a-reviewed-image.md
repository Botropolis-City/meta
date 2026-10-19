# 135. make publishable can fail on an image that is on the reviewed list

**Open, in progress since 2026-10-19 in the session "item 135". Filed 2026-10-19 (r685), from item 99. Nobody's call — a defect.**

Depends on: nothing

`botropolis/tools/check-publishable` failed once saying `docs/screenshots/r460-item-87-new-session.png` "is not on the reviewed list" though it is, then passed three times in a row (item 99, 2026-10-19).
The script runs under `set -o pipefail`, and line 251 reads `printf '%s\n' "${reviewed}" | grep -qxF "${img}"`: `grep -q` exits on its first match, and if `printf` is still writing it dies of SIGPIPE, so the pipeline fails although grep matched.
The longer the reviewed list and the earlier the image sits in it, the likelier it is; a guard that fails for nothing teaches everyone to rerun rather than read.

## The fix

Match without a pipe — `grep -qxF -- "${img}" <<<"${reviewed}"`, or an associative array built once — and look for the same `printf | grep -q` shape elsewhere in `botropolis/tools/` and in the meta repository's `tools/`.

Tests: an acceptance case that runs the check with a reviewed list long enough to make the race near-certain (tens of thousands of lines, the image first) and expects it to pass every time over many runs; red before the fix.
