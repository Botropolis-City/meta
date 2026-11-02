# 317. KEEP_ON_FAILURE=0 keeps the box

**Fixed 2026-11-02 (`3383047`, r1212 of meta). Filed 2026-10-28 (r1197), caught by the performance manager before ordering 0.3.3's third soak. Nobody's call — a defect.**

`testing/machines/Makefile` passes `--keep-on-failure` when `${KEEP_ON_FAILURE}` is non-empty, so `KEEP_ON_FAILURE=0`, the natural way to say *don't keep it*, keeps a failed box billing until its booked cancellation.

## The fix

Keep the box only for `KEEP_ON_FAILURE=1`; refuse any other non-empty value, naming the two the Makefile takes; say so in the README; and a test that `=0` and unset both cancel on failure, and `=1` keeps.

## Closed

`testing/machines/Makefile` passes `--keep-on-failure` only for `KEEP_ON_FAILURE=1`.
`=0` or unset cancels,
and any other value, including one with two words, stops make before anything runs, naming `=1` and `=0`.
The README says so,
and `testing/machines/makefile_test.py` dry-runs the Makefile for unset, `0`, `1` and five refused values.
