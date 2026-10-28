# 313. i3 dies on the soak box as it starts, and the set-up says it started

**Open, in progress since 2026-10-28 in the session "item 313". Filed 2026-10-28 (r1196), from 0.3.3's second soak, whose pre-flight (item 309) failed in its first minutes as designed. Nobody's call — a defect.**

The pre-flight on server 3101910 failed with *i3-msg did not run on display ':0'*.
The box's `/home/soak/i3.log` says why: `[libi3] ERROR: mkdir(/run/user/0/i3) failed: Permission denied`, then `Segmentation fault`.
`testing/machines/soak/setup` starts i3 with `runuser -u soak -- env DISPLAY=:0 HOME=/home/soak setsid i3`, which keeps root's `XDG_RUNTIME_DIR=/run/user/0`, a directory the soak user cannot write; and it prints *setup: i3 started* without checking that i3 is still running.
Soak 5 (server 3101537) printed the same line and could never find or hide its window either, so this is likely the same fault there, behind the missing `xprop` that item 309 fixed.

## The fix

1. Start i3 (and anything else run as `soak`) with a runtime directory the soak user owns: `XDG_RUNTIME_DIR` unset or set to a `0700` directory owned by `soak`.
2. After starting i3, wait for `i3-msg -t get_version` to answer on `:0` as `soak`, and fail the set-up, naming `i3.log`'s last lines, if it does not within a few seconds; print *i3 started* only then.
3. Tests: the set-up's i3 launch does not pass root's runtime directory; a set-up whose i3 exits at once fails, naming the log, instead of reporting it started.
