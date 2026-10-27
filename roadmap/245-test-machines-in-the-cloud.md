# 245. The tests that need another desktop or a whole night have no machine to run on

**Open. Filed 2026-10-25 (r1024) at Aria's request. Nobody's call — Aria chose the providers and where the code lives; the run waits on her Hetzner account.**

Depends on: 266
Landed: slice 1 (`2b502b8`, r1032).
Landed: slice 2 (`a2c45ad`, r1066).
Landed: slice 3 (`88adaa0`, r1096).

Aria, 2026-10-25, on how to test items 95 and 96 without owning a Mac or a Wayland desktop: *"I won't suddenly own one of these. We need a vm to test."*
And on item 164's overnight soak, which needs a screen that never blanks or locks: *"I meant remote vm like in linode or gcp or some other cloud env or maybe a cloud intended for perf or cross platform testing"*.

Three tests have nowhere to run:
- [item 164](164-no-soak-test-for-the-growth-budget.md)'s 8-hour soak (`performance/tools/perf-soak`, which takes `--display` and `--no-hide`) needs a visible X session that never locks, with a GPU on a Mesa driver so its GPU memory means what it does on Aria's laptop;
- [item 96](096-the-global-shortcut-on-wayland.md) needs GNOME 48 or later and KDE Plasma 6 Wayland sessions, with keys injected and screens captured;
- [item 95](095-the-global-shortcut-on-macos.md) needs macOS 14 or later with a GUI. It is not this item's: GitHub's hosted macOS runners serve it, from its own workflow.

## What Aria chose (2026-10-25)

- **The soak** runs on **the soak box**: a dedicated server from Hetzner's server auction with an Intel Core 12th gen or later iGPU (UHD 770 or newer on Mesa's `iris`, the GPU of the EX44 first chosen), billed by the hour with no setup fee, about €1.76 for a 10-hour run. Real Xorg with the `modesetting` driver on the iGPU and a forced EDID, i3, `xset s off -dpms` and no locker. Not VirtualGL, which copies each frame into the process's memory and changes what the soak measures; not Xvfb with llvmpipe, which hides GPU memory inside the process.
- **The Wayland desktops** run on a **Hetzner Cloud** VM, Fedora Workstation for GNOME and Fedora KDE for Plasma 6, each autologged into a normal session (KRdp has no headless mode). Keys go in over SSH through `ydotool` (uinput, below the compositor); screens come out through the screenshot portal or `spectacle -b`; the `BindShortcuts` confirmation dialog is accepted with keys.
- **The code lives in the meta repository, at `testing/machines/`**: `hcloud` Terraform for the cloud VM, and a reviewed script against Hetzner's Robot API for the soak box, which has no official Terraform provider. Nothing applies on push. A run is plan, Aria's approval, apply, test, destroy, and the destroy runs even when the test fails.
- **Secrets by reference only**: the Hetzner tokens come through `secret-run --env …=op:…`, never on a command line.

## The fix

1. `testing/machines/` with the Terraform, the Robot API script, the guest set-up (cloud-init or a script kept beside it), and a `Makefile` whose targets are `plan`, `apply`, `run-soak`, `run-wayland` and `destroy`, each saying what it will cost before it spends.
2. Tests that need no account: the Terraform validates and formats; the scripts' `--help` and their refusal to run without a token reference; a teardown that runs when the test step fails.
3. **Stop at the plan** until Aria has created the Hetzner account and named the token's 1Password reference; then `terraform plan` for her to read, and nothing applied without her.
4. Once applied once: check `/dev/dri` on the soak box before the first soak, since Hetzner may not leave the iGPU enabled, and say what was found here.

Research, with sources, is in items 95 and 96's *Testing without the hardware* sections; prices are as found on 2026-10-25.
The machines, and how a run goes, are in [testing/machines](../testing/machines/README.md).

## Slice 3: a soak that survives losing its connection

The first overnight soak (2026-10-26, auction server 3100438, 04:01 to 10:49) died at about 6¾ of its 8 hours, and its report died with it.
The laptop slept at 10:41 and woke on Wi-Fi with no IPv6, after the mobile link that had carried the IPv6-only box's address went down.
The soak ran as the foreground command of one `ssh`, so the session's loss ended it (`perf-soak exited 255`); the report lived only on the box, in the rescue system's RAM; the fetch then failed (`Network is unreachable`), and the runner's `finally` cancelled the box anyway, as it is written to.
Nothing about botropolis failed that anyone knows of; the cost was about EUR 1.20 and the night.

Aria, 2026-10-26, chose to fix the runner before the soak is ordered again.
The runner (`testing/machines/machines`, `run_soak`) needs to:

1. **Run the soak detached on the box**, under `setsid` or a systemd transient unit there, so it survives the ssh session, and reconnect to watch it rather than hold one connection for eight hours.
2. **Fetch the report as it grows**, every hour and at the end, so a lost box loses at most an hour.
3. **Never cancel a box it could not fetch from** while the box is billing under the run's ceiling: retry the fetch, with backoff, for a bounded time (say an hour), then say loudly that the box is left up and how to fetch and cancel it, rather than cancel it silently. The ceiling on cost still holds: the runner cancels once the run's time and price limit is reached, fetched or not, and says what was lost.
4. **Refuse to start an IPv6-only box from a machine with no IPv6 route**, and say to add `IPV4=1`, rather than order a box it cannot reach.

The tests pin each against a fake transport: a dropped session mid-soak, a fetch that fails then succeeds, a fetch that never succeeds before the ceiling, and a planning machine with no IPv6 route.

## Answered while building

- **The plan and tree** (manager, 2026-10-25): approved. One stdlib Python CLI and a Makefile in `testing/machines/`; a real soak box order only after Aria types the hourly price back, and `terraform apply` without `-auto-approve`; destroy in a `finally` that runs on failure and on interrupt.
- **Network in `make test`** (manager): none. Terraform validates only against a provider already cached and says loudly when it skipped; `make validate` there fills the cache for a human.
- **The EX44's system** (manager): Arch, so its Mesa matches Aria's laptop and the GPU figure compares.
- **Whose sessions the soak replays** (manager, from the standing rule that nothing derived from `~/.claude` is copied): the demo's alone, and the report says so; nothing of Aria's history goes to a rented machine.
- **IPv4** (manager): IPv6-only by default, since this machine reaches IPv6 (over its mobile link), with `IPV4=1` adding Hetzner's paid address for a network without it.
- **Token references** (manager): Makefile variables with no default, set in a git-ignored `testing/machines/.env`, so nothing public names Aria's vault.
- **A history of real size** (manager, 2026-10-25, from a side agent's note to Aria): demo sessions alone would miss growth that scales with history, so the soak stages a synthetic home of at least 200 sessions in 150 projects, the size of Aria's, from the generator the cost tests use (`testing/helpers/fixtures.go`), with the demo's writers on top; its report names the counts and says the history was synthetic. A run on Aria's own machine with her real history stays possible before a release, with `--keep-awake` restored, if she asks for one.
- **Where the synthetic history comes from** (manager, 2026-10-25): `botropolis-demo synth-home`, filed as [item 248](248-a-synthetic-history-cannot-be-made-outside-go-test.md) since this item works only in the meta repository; `run-soak` takes a required `--history DIR`, refuses a path inside the real `~/.claude`, uploads it as the soak user's history under the demo's writers, and writes its counts into the report.
- **The account** (Aria, 2026-10-26): created, with a Hetzner Cloud project and its API token in 1Password; its reference is set in the git-ignored `testing/machines/.env` (no public file names the vault), and it resolves. The soak box is ordered through Hetzner Robot, which takes a separate web-service user and password, still to be created; until then only the Wayland VM can be planned.
- **What the soak box really costs** (manager, 2026-10-26, from Robot's ordering API on Aria's account, which charges no VAT): the EX44 is not orderable through the API at all, and every standard product with an integrated GPU carries a setup fee per order (AX42-1 €59 + €0.1877/h, EX63-1 €84 + €0.2758/h, so €61–87 a run), which the runner already refuses. The server auction lists used machines by the hour with no setup fee, among them a Core i5-12500 (Intel UHD 770 on `iris`, the EX44's own GPU) at €0.1763/h, about €1.76 for a ten-hour run.
- **The soak box** (Aria, 2026-10-26): the auction. The runner chooses, at order time, the cheapest auction server with an Intel integrated GPU and no setup fee, shows it and its price in the plan, and orders only after the price is typed back; it refuses anything with a setup fee or no hourly price.
- **Slice 2's tree and two findings** (manager, 2026-10-26): every auction listing boots only Hetzner's rescue system, so the run installs Arch minimal with `installimage` from rescue before the set-up, and a failed install cancels the server. The auction's cheapest Intel iGPUs are Skylake-era; the rule is pinned to the EX44's generation, Intel Core 12th gen and later with an iGPU, since Aria chose the box for that GPU and Mesa driver (and her laptop is Xe-class). The plan is saved and re-read at apply, which refuses a listing that is gone, repriced or now charges setup.
- **Which system the soak box runs** (Aria, 2026-10-26, asked by the manager): straight in Hetzner's rescue system, with no install and no reboot; Xorg, i3 and Mesa go into the Debian-based rescue system's RAM. Its Mesa is older than Aria's laptop's, so `machine.txt` records the version and the GPU memory figure is read against it; the soak's main question, the city's and the daemon's own memory growth, does not depend on it.
- **The SSH key** (Aria, 2026-10-26, asked by the manager): Robot refuses even a test order naming a key it does not hold, so the plan uploads one first; it is a dedicated key, `~/.ssh/botropolis-machines`, created by the runner if missing, whose public half alone goes to Robot as `botropolis-machines`. Aria's personal keys are never read or uploaded. The plan found auction server 3100438, a Core i5-12500 in Falkenstein, at €0.1763 an hour with no setup fee.
- **Slice 3's design and tree** (manager, 2026-10-26): approved: the soak starts detached with `setsid` and writes its exit code to a file the runner polls over fresh connections; the report is fetched hourly into staging and merged only on success; a machine with no IPv6 route is refused before any secret or request unless `IPV4=1`. A fetch that keeps failing is retried with backoff until it succeeds or the run's ceiling (`--max-hours`, 10 by default, from delivery) is reached, and then the box is cancelled, fetched or not, with what was lost said; there is no state in which the box is left up unwatched, because the item holds the cost ceiling. Ctrl-C makes one fetch attempt, then cancels.
- **The soak depends on the box alone** (Aria, 2026-10-26: *"we shouldn't tie the 8 hour soak to this laptop. It should only depend on that server"*; she chose a box that cancels itself and uploads its report, to Cloudflare R2, item 266): slice 3 changes. The box uploads its report to item 266's bucket hourly and at the end, with the bucket-scoped write credential the runner hands it; at order time the runner also books Robot's cancellation for the next date it allows (`POST /server/{n}/cancellation` with a date, after reading `earliest_cancellation_date`), so the box stops billing with no laptop; the laptop, if it is up, watches, fetches from the bucket and cancels early. The runner's fetching from the box stays only as a fallback. Slice 3 depends on item 266 for the real run; its tests use a fake bucket.
- **Which date the box books its cancellation for** (manager, 2026-10-26, asked by the session; Robot's docs say days, and not whether a date cancels at its start or end): max(`earliest_cancellation_date`, the date of delivery plus `--max-hours`, plus one day), since a soak cut short wastes the run and the worst case unwatched, about EUR 10, is under the $20 a run Aria allowed. The booked date and when the box went away go in `machine.txt`, and the margin is tightened once a real run shows Robot's behaviour. An early cancel revokes the booking (`DELETE`) and then cancels `now`, since a POST over a booking is a 409. The bucket is read through `.env`'s `BUCKET_URL`, `BUCKET_WRITE_ID_REF`, `BUCKET_WRITE_SECRET_REF`, `BUCKET_READ_ID_REF` and `BUCKET_READ_SECRET_REF`, which item 266 fills.
- **A small follow-up for the runner** (performance manager, 2026-10-27): `clock()` prints the laptop's local time with no offset, beside the set-up's `+01:00` Berlin times in the same pane, which led two readers to misread the soak's ceiling; print every time with its offset (`astimezone().isoformat()`).
