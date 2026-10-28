# 317. KEEP_ON_FAILURE=0 keeps the box

**Open. Filed 2026-10-28 (r1197), caught by the performance manager before ordering 0.3.3's third soak. Nobody's call — a defect.**

`testing/machines/Makefile` passes `--keep-on-failure` when `${KEEP_ON_FAILURE}` is non-empty, so `KEEP_ON_FAILURE=0`, the natural way to say *don't keep it*, keeps a failed box billing until its booked cancellation.

## The fix

Keep the box only for `KEEP_ON_FAILURE=1`; refuse any other non-empty value, naming the two the Makefile takes; say so in the README; and a test that `=0` and unset both cancel on failure, and `=1` keeps.
