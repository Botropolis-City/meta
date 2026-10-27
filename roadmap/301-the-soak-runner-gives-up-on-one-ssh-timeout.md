# 301. The soak runner gives up the whole run on one ssh timeout while copying to the box

**Open. Filed 2026-10-27 (r1179), from 0.3.3's first soak. Nobody's call — a defect in the runner.**

0.3.3's first soak box (auction server 3100496) came up at 08:11:41 and ran its set-up, an apt install of Xorg, i3 and Mesa; the next ssh, copying `performance/` to the box, timed out in the banner exchange about a minute later ("Connection timed out during banner exchange"), and the runner cancelled the box: nothing soaked, about EUR 0.18 spent, and a reorder.
The set-up's own ssh had worked, so the stall was transient, perhaps sshd restarting during the package upgrade.

`run_soak` in `testing/machines/machines` retries reaching the box only in `wait_for_ssh`; every later `ssh` and `scp` is tried once.

## The fix

Give every ssh and scp to the box after delivery the same patience `wait_for_ssh` has: a few attempts over a minute or two on a connection failure (exit 255, a banner or connect timeout), never on the remote command's own failure; and after the set-up, wait for sshd to answer before copying.
Tests, against the fake transport: an scp that fails twice with a timeout and then succeeds goes on; one that keeps failing gives up after its attempts and cancels; a remote command that exits non-zero is not retried.
