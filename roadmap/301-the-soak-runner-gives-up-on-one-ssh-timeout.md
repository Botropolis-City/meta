# 301. The soak runner gives up the whole run on one ssh timeout while copying to the box

**Open, in progress since 2026-10-27 in the session "item 301". Filed 2026-10-27 (r1179), from 0.3.3's first soak. Nobody's call — a defect in the runner.**

0.3.3's first soak box (auction server 3100496) came up at 08:11:41 and ran its set-up, an apt install of Xorg, i3 and Mesa; the next ssh, copying `performance/` to the box, timed out in the banner exchange about a minute later ("Connection timed out during banner exchange"), and the runner cancelled the box: nothing soaked, about EUR 0.18 spent, and a reorder.
The set-up's own ssh had worked, so the stall was transient, perhaps sshd restarting during the package upgrade.

`run_soak` in `testing/machines/machines` retries reaching the box only in `wait_for_ssh`; every later `ssh` and `scp` is tried once.

## The fix

Give every ssh and scp to the box after delivery the same patience `wait_for_ssh` has: a few attempts over a minute or two on a connection failure (exit 255, a banner or connect timeout), never on the remote command's own failure; and after the set-up, wait for sshd to answer before copying.
Tests, against the fake transport: an scp that fails twice with a timeout and then succeeds goes on; one that keeps failing gives up after its attempts and cancels; a remote command that exits non-zero is not retried.

## Worse than a blip (performance manager, 2026-10-27)

The reorder (server 3100616, another datacentre) failed the same way: the set-up's output stops at the end of its apt install, "Regenerating fonts cache... done.", none of its later steps (the \`/dev/dri\` report, the forced EDID, Xorg) print anything, and the box stops answering ssh for minutes; two boxes, about EUR 0.35.
On 2026-10-26 an identical i5-12500 got through every step.
\`soak/setup\` has not changed since; the runner has (item 245's slice 3: the detached run, the bucket, the self-booked cancellation), and both failing boxes were ordered with \`IPV4=1\`, where the 26th's was IPv6-only.
Because the runner cancels a box the moment a step fails, nothing could be looked at.

So this item now also:
1. finds why the box goes silent after its apt step: what slice 3 runs between the set-up and the copy; whether the set-up's later steps (writing the EDID override through debugfs, starting Xorg) can wedge the rescue kernel or its network, for instance with an IPv4 address added; and anything else that differs from the 26th;
2. gives the runner a way to keep a box on failure (\`--keep-on-failure\`, still bound by the booked cancellation) and to fetch the set-up's log and \`dmesg\` before cancelling, so the next failure can be seen;
3. keeps the retry this item began with.
Aria, 2026-10-27, chose to release 0.3.3 without waiting, and to run its soak once this is fixed.
