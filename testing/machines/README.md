# Test machines

The machines for the tests that need another desktop or a whole night ([item 245](../../roadmap/245-test-machines-in-the-cloud.md)).
Each is rented from Hetzner by the hour, made for one run and destroyed after it.

| machine | what it is | for |
| --- | --- | --- |
| `soak` | the soak box: a dedicated server from Hetzner's server auction with an Intel Core 12th gen or later iGPU (UHD 770 or newer on Mesa's `iris`), ordered through the Robot API | [item 164](../../roadmap/164-no-soak-test-for-the-growth-budget.md)'s 8-hour soak |
| `wayland` | a Hetzner Cloud VM running Fedora with GNOME or KDE Plasma 6 on Wayland, made by Terraform in `cloud/` | [item 96](../../roadmap/096-the-global-shortcut-on-wayland.md)'s global shortcut |

## A run

A run is plan, approval, apply, test, destroy, and the destroy runs when the test fails and when the run is interrupted.

```
make plan MACHINE=soak                   # choose the soak box, its price, and a test order Hetzner does not process
make run-soak PERF_BUILD=dir             # order the planned box, set up, soak 8 hours, fetch the report, cancel
make plan MACHINE=wayland DESKTOP=kde    # the price, and terraform plan
make run-wayland DESKTOP=kde SCRIPT=file # make the VM, run SCRIPT in the session, fetch results, destroy
make run-soak PERF_BUILD=dir KEEP_ON_FAILURE=1  # the same, but a box that fails before its soak stays up to be looked at
make destroy MACHINE=soak                # cancel by hand, if a run could not
make destroy MACHINE=soak SERVER=4242    # the same, naming the box when several are recorded
```

Every target that spends says what it will cost first.
Nothing applies on its own, and nothing applies on push:
the soak box is ordered only after its hourly price is typed back at the terminal,
and the VM only after Terraform's own `yes`.
The runner refuses a soak box that is not billed by the hour or has a setup fee, because either would cost far more than a run.

Results land in `$XDG_STATE_HOME/botropolis-perf/`, with a `machine.txt` saying what ran where.

Each soak order keeps its own record, `$XDG_STATE_HOME/botropolis-machines/soak-<listing>.json`, and a run cancels only the box in its own record, so two soaks can run side by side ([item 310](../../roadmap/310-a-second-soak-would-cancel-the-first-ones-box.md)).
`apply` refuses to replace a record whose server Robot still lists, naming the box, and orders nothing.
A `soak.json` left by a runner from before this is never written or moved, so the run that wrote it still cancels its own box,
and `make destroy` finds it like any other record.
With one record, `make destroy MACHINE=soak` cancels that box;
with several, it cancels none and lists them, and `SERVER=N` names the one to cancel.
Cancelling by hand is `make destroy`; if that fails too, it says so loudly, and the machine is cancelled in Robot or the Cloud console.

## Secrets

The tokens are passed by reference only, to `secret-run`, never by value.
Put the references in `testing/machines/.env`, which git ignores, so the public repository never names a vault:

```
ROBOT_USER_REF=op:Vault/Item/username
ROBOT_PASSWORD_REF=op:Vault/Item/password
HCLOUD_TOKEN_REF=op:Vault/Item/token
BUCKET_URL=https://ACCOUNT.r2.cloudflarestorage.com/BUCKET
BUCKET_WRITE_ID_REF=op:Vault/Item/write-id
BUCKET_WRITE_SECRET_REF=op:Vault/Item/write-secret
BUCKET_READ_ID_REF=op:Vault/Item/read-id
BUCKET_READ_SECRET_REF=op:Vault/Item/read-secret
```

The bucket's keys come from item 266: a write-only key the soak box uploads with, and a read-only key the laptop fetches with.

The Robot user is a web service user, made in Robot under *Settings, Web service and app settings*, with ordering enabled.
The machines are reached with the runner's own key, `~/.ssh/botropolis-machines`, never your personal one.
The runner makes it when it is missing, with no passphrase so an overnight run needs nobody, and readable by you alone.
The first plan uploads its public half to Robot's key store as `botropolis-machines`, since even a test order may only name keys Robot holds.
The Wayland VM's Terraform is given the same key.

## The soak machine

The soak box comes from Hetzner's server auction, since the EX44 first chosen cannot be ordered through the API and every standard product with an iGPU has a setup fee.
`make plan MACHINE=soak` reads the auction and chooses the cheapest listing whose CPU is an Intel Core of the 12th generation or later with graphics (no F part), billed by the hour with no setup fee.
It prints the listing's id, CPU, datacenter, hourly and monthly price and setup fee,
sends Robot a test order for it,
and saves the choice in `$XDG_STATE_HOME/botropolis-machines/soak-plan.json`.
`apply` and `run-soak` order that listing and no other:
they re-read it and refuse if it is gone, has a setup fee, has no hourly price or costs anything other than the plan said.
Auction prices drop on a schedule, so a drop since the plan refuses too; plan again.

The auction delivers the box booted into Hetzner's rescue system, which is Debian and runs from RAM, and the soak runs right there, with nothing installed to disk and no reboot.
`soak/setup` turns the rescue system into the soak's display:
it installs Xorg, i3, Mesa, botropolis's libraries and the X tools that hide the window (`xprop` and `xwininfo` from `x11-utils`, `xset` from `x11-xserver-utils`) with apt,
forces a 1920x1080 display on with an EDID from `edid.py` through the DRM debugfs `edid_override`, since the kernel command line cannot change without a reboot,
and starts Xorg with the `modesetting` driver on the iGPU, i3, `xset s off -dpms` and no locker.
`soak/start-i3` starts i3 as the soak user with its own runtime directory, `/run/soak`, since root's `/run/user/0` is not writable by soak and i3 dies without one (item 313).
The set-up says i3 started only once `i3-msg -t get_version` answers on `:0`, and otherwise exits 5 and quotes the end of `i3.log`.
The pre-flight and the soak run with the same `XDG_RUNTIME_DIR`.
It writes what it found in `/dev/dri`, the Mesa version and the renderer to `dri.txt` in the results, and stops if there is no iGPU, since Hetzner may not leave it enabled.
`machine.txt` names the rescue system's Mesa version, since it is Debian's and not the one on Aria's laptop.
A failed set-up cancels the box like any other failure.

Once the files are copied and before the soak starts, the runner runs `perf-soak --preflight` as the soak user on `:0` ([item 309](../../roadmap/309-the-soak-box-cannot-hide-the-city.md)).
It checks that `xprop`, `xwininfo`, `i3-msg` and `xset` are installed and reach the display,
then opens the city for a minute and finds its window, hides it and shows it again.
0.3.3's soak ran four hours before it found it could not hide the window, because the set-up had left out `x11-utils`.
A pre-flight that fails stops the run before the soak, with its diagnostics, and the box is cancelled or, with `KEEP_ON_FAILURE=1`, kept.
`machine.txt` records the pass.
A soak that will hide the window also checks for those tools itself when it starts, and exits 2 at once, naming the missing one.

### When the box goes quiet

0.3.3's first two soak boxes stopped answering ssh right after a set-up that had succeeded, and each was cancelled before anything could be seen ([item 301](../../roadmap/301-the-soak-runner-gives-up-on-one-ssh-timeout.md)).
The cause, from a kept box's sshd log: an ssh brute-force bot found the box's fresh IPv4 address within minutes, and the rescue system's sshd, at the default `MaxStartups` of 10:30:100, then dropped new connections at random, the runner's among them.
The 26th's box was IPv6-only and was never scanned.
So:

- **The box's ssh is closed to everyone but the runner**, first thing after it answers and before anything else runs there. The runner asks the box where it connects from (`SSH_CLIENT`, never a web service), and `soak/lockdown`, sent on ssh's standard input, accepts port 22 from that address alone, or its /64 for IPv6, drops it from everyone else with iptables-legacy (the rescue kernel has no nf_tables, so nft is only the fallback), turns off password logins and reloads sshd. `machine.txt` records who may reach the box. If the laptop's address changes during the soak, it cannot reach the box any more, but the soak goes on and the bucket still has its report.
- **One connection carries every ssh and scp** after that (`ControlMaster`), so the box sees one connection instead of dozens; the runner closes it at the end.
- **Every ssh and scp to the box is patient.** A connection failure (exit 255) is tried again, five times, `MACHINES_POLL_SECONDS` apart (`MACHINES_SSH_ATTEMPTS` changes the count). A remote command's own failure is never retried. The set-up can be run twice, and the soak's start is guarded by `/root/soak.started`, so a retry cannot start it twice. After the set-up, the runner waits for ssh to answer before it copies.
- **The set-up says each step** after apt, and keeps all it says in `/root/setup.log` on the box.
- **`box.log` in the results** holds the box's kernel log and a heartbeat (load and memory) every five seconds, streamed over one ssh from just after delivery until the soak starts. If the box wedges, its last words are on the laptop, and the heartbeat says when it stopped.
- **A failure before the soak starts collects diagnostics** before the box goes: a ping, then `setup.log`, `dri.txt`, the Xorg and i3 logs, `dmesg`, `ip addr`, `free` and `ps`, into `diagnostics/` in the results. Whatever could not be collected is said.
- **`KEEP_ON_FAILURE=1`** leaves a box that failed before its soak started up for you to look at, until its booked cancellation, which can be up to a day. The runner says the date, the most it costs, how to reach it and how to cancel it sooner, and `machine.txt` records it. An interrupt and the ceiling still cancel.

### The soak depends on the box alone

The first overnight soak, on 2026-10-26, died when the laptop that held its ssh session dropped its IPv6, and its report died with it.
So the soak no longer needs the laptop once it has started (item 245, slice 3):

- **The box stops billing on its own.** Right after delivery, `apply` books Robot's cancellation for the day after `MAX_HOURS` (10 by default) from delivery, Berlin time, or Robot's earliest date if that is later. A box no one ever cancels runs at most to the end of that day, about EUR 10. If the booking fails, the box is cancelled at once.
- **The soak runs detached** under `setsid`, through `soak/detached`, so losing the connection does not end it.
- **The box uploads its report** to the soak bucket ([item 266](../../roadmap/266-the-soak-box-has-nowhere-to-leave-its-report.md)) as `<run>/report.tar.gz` every hour and at the end, and then the exit code as `<run>/exit`. It signs with a write-only key that the runner writes to `/root/bucket.env`, mode 600, through ssh's standard input, so the key is never in an argument list or on the laptop's disk. `s3.py` signs the requests with nothing but Python's standard library, so the box needs no S3 client.
- **The laptop, while it is up**, watches the bucket for the exit code with a read-only key, fetches the report every hour and at the end, and then cancels early. Cancelling early means revoking the booking and cancelling `now`, since Robot refuses to cancel a server already booked for cancellation. If Robot will not revoke it, the runner says so loudly, with the date and what it costs.
- **Fetching over ssh is the fallback**, for a report the bucket does not answer with. A fetch lands in a staging directory first, so one that drops halfway leaves the last good copy as it was.

A failed final fetch is retried with backoff, up to five minutes apart, until `MAX_HOURS`; the box is then cancelled, fetched or not, and the runner says what was lost and where the bucket keeps it.
Interrupting a run makes one fetch and then cancels.
`machine.txt` records the booked date, the run's name in the bucket and when the box was cancelled.
After the first real run, check there when Robot ended a booked server, at the start or the end of its day, since its documentation does not say.

The soak runs on a synthetic history of 200 sessions in 150 projects, made by `botropolis-demo synth-home` ([item 248](../../roadmap/248-a-synthetic-history-cannot-be-made-outside-go-test.md)).
Nothing from a real `~/.claude` goes to a rented machine: the runner refuses one.

The soak box is ordered without the paid IPv4 address.
This was decided on a machine whose IPv6 came over a mobile link (`wwan0`); on a network without IPv6, add `IPV4=1`.
The runner checks for an IPv6 route before it plans, orders or runs a soak box without IPv4,
and refuses, naming `IPV4=1`, rather than order a box it cannot reach.

## The Wayland machine

The VM is Fedora 42 (GNOME 48, Plasma 6), turned into a desktop by `cloud/cloud-init.yaml.tftpl`:
the desktop logs `tester` in automatically, never locks, and runs `ydotool`, so keys go in below the compositor.
`SCRIPT` runs as `tester` inside that session, with `RESULTS` naming the directory that comes back.

## Checking it without an account

`make test` at the root checks the runner against stubs and a fake Hetzner, formats the Terraform, and shellchecks the set-up.
It validates the Terraform only when the hcloud provider is already cached, and says so when it is not.
`make validate` here caches it, which needs the network but no account.
