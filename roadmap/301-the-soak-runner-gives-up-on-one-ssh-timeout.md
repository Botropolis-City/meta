# 301. The soak runner gives up the whole run on one ssh timeout while copying to the box

**Open, in progress since 2026-10-27 in the session "item 301". Filed 2026-10-27 (r1179), from 0.3.3's first soak. Nobody's call — a defect in the runner.**

0.3.3's first soak box (auction server 3100496) came up at 08:11:41 and ran its set-up, an apt install of Xorg, i3 and Mesa; the next ssh, copying `performance/` to the box, timed out in the banner exchange about a minute later ("Connection timed out during banner exchange"), and the runner cancelled the box: nothing soaked, about EUR 0.18 spent, and a reorder.
The set-up's own ssh had worked, so the stall was transient, perhaps sshd restarting during the package upgrade.

`run_soak` in `testing/machines/machines` retries reaching the box only in `wait_for_ssh`; every later `ssh` and `scp` is tried once.

## The fix

Give every ssh and scp to the box after delivery the same patience `wait_for_ssh` has: a few attempts over a minute or two on a connection failure (exit 255, a banner or connect timeout), never on the remote command's own failure; and after the set-up, wait for sshd to answer before copying.
Tests, against the fake transport: an scp that fails twice with a timeout and then succeeds goes on; one that keeps failing gives up after its attempts and cancels; a remote command that exits non-zero is not retried.

## Worse than a blip (performance manager, 2026-10-27)

The reorder (server 3100616, another datacentre) failed the same way: the set-up's output stops at the end of its apt install, "Regenerating fonts cache... done.", none of its later steps (the `/dev/dri` report, the forced EDID, Xorg) print anything, and the box stops answering ssh for minutes; two boxes, about EUR 0.35.
On 2026-10-26 an identical i5-12500 got through every step.
`soak/setup` has not changed since; the runner has (item 245's slice 3: the detached run, the bucket, the self-booked cancellation), and both failing boxes were ordered with `IPV4=1`, where the 26th's was IPv6-only.
Because the runner cancels a box the moment a step fails, nothing could be looked at.

So this item now also:
1. finds why the box goes silent after its apt step: what slice 3 runs between the set-up and the copy; whether the set-up's later steps (writing the EDID override through debugfs, starting Xorg) can wedge the rescue kernel or its network, for instance with an IPv4 address added; and anything else that differs from the 26th;
2. gives the runner a way to keep a box on failure (`--keep-on-failure`, still bound by the booked cancellation) and to fetch the set-up's log and `dmesg` before cancelling, so the next failure can be seen;
3. keeps the retry this item began with.
Aria, 2026-10-27, chose to release 0.3.3 without waiting, and to run its soak once this is fixed.

## What the two failures show (2026-10-27)

The set-up did not go quiet after its apt step: it finished, and exited 0.
Its later steps write to `dri.txt` and never to its output, so a silent console is what a good set-up looked like.
The runner got past its check of the set-up's exit,
and box 3100616's `machine.txt` has the Mesa version, which comes from a separate ssh made after the set-up,
so X and i3 were up and one more ssh worked.
The next connection, the copy of `performance/`, failed with "Connection to … port 22 timed out", and box 1's with "timed out during banner exchange".
Both come from OpenSSH after the TCP connection is made, unlike "ssh: connect to host … Connection timed out" for a host that does not answer at all:
the box's kernel still took the connection,
and sshd never spoke.
That points at a stall in the box's userspace after X and i3 started (memory, a process stuck in the kernel on i915, sshd unable to fork) more than at its network.
Item 245's slice 3 changed nothing between the set-up and the copy: `run_soak` there is the 26th's, apart from the files copied before the set-up, and `soak/setup` is unchanged.
What did change: `IPV4=1`, a different board and datacentre (FSN1-DC2 and DC13, not DC3; an ASUSTeK board with DP-1 forced), and perhaps the rescue kernel (6.12.67; the 26th's `dri.txt` died with its report).
Nothing on the laptop can tell these apart,
so the fix instruments, retries and keeps,
and the next run names the cause.
What it does is in [testing/machines/README.md](../testing/machines/README.md#when-the-box-goes-quiet).

## The cause (manager, 2026-10-27)

The diagnostic run's box, server 3100620, was kept, and its sshd log names it: an ssh brute-force bot found the box's fresh IPv4 address within minutes and tried a password every two to five seconds, for root, pi, deploy, toor and the rest.
The rescue system's sshd runs at the default `MaxStartups` of 10:30:100,
so with the bot's unauthenticated connections open,
it drops new ones at random, which gave the runner its banner and connect timeouts while the box answered ping and was otherwise healthy.
The 26th's box was IPv6-only and was never scanned.

So a second slice closes the box's ssh to the runner alone, before anything else runs there,
and carries every later ssh and scp over one shared connection;
the retries stay.

## Decided

- **The diagnosis, the fix, the instruments and the test tree** (manager, 2026-10-27): approved.
- **Keeping a failed box** (manager, 2026-10-27): opt-in, `KEEP_ON_FAILURE=1`, since a kept box bills until its booked date, up to a day. The manager passes it for the diagnostic run.
- **The retry budget** (manager, 2026-10-27): five attempts over about two minutes, configurable with `MACHINES_SSH_ATTEMPTS`.
- **An IPv6-only datapoint** (manager, 2026-10-27): not possible from the laptop today, which has no IPv6 route.
- **The second slice** (manager, 2026-10-27): right after the box answers ssh, close port 22 to the runner's own address and turn off password logins; one multiplexed connection for every ssh and scp after that; keep the retries. The runner learns its address from the box's own view of the connection (`SSH_CLIENT`), not from a web service. For IPv6 it opens the /64, since the laptop's temporary addresses rotate during an eight-hour run.
- **Which firewall** (manager, 2026-10-27, from kept box 4): the rescue kernel, 6.12.67, has `ip_tables` but no `nf_tables`, so `nft` and the nft-backed `iptables` both fail there ("cache initialization failed: Invalid argument"). `iptables-legacy` worked: with the runner's address accepted and port 22 dropped for the rest, the bot's failed passwords stopped within 30 seconds and the runner's ssh carried on. So the lock-down uses `iptables-legacy` and `ip6tables-legacy` first, and nft only where they are missing.
