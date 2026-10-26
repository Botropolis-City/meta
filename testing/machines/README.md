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
make run-soak PERF_BUILD=dir             # order the planned box, install Arch, set up, soak 8 hours, fetch the report, cancel
make plan MACHINE=wayland DESKTOP=kde    # the price, and terraform plan
make run-wayland DESKTOP=kde SCRIPT=file # make the VM, run SCRIPT in the session, fetch results, destroy
make destroy MACHINE=soak                # cancel by hand, if a run could not
```

Every target that spends says what it will cost first.
Nothing applies on its own, and nothing applies on push:
the soak box is ordered only after its hourly price is typed back at the terminal,
and the VM only after Terraform's own `yes`.
The runner refuses a soak box that is not billed by the hour or has a setup fee, because either would cost far more than a run.

Results land in `$XDG_STATE_HOME/botropolis-perf/`, with a `machine.txt` saying what ran where.
Cancelling by hand is `make destroy`; if that fails too, it says so loudly, and the machine is cancelled in Robot or the Cloud console.

## Secrets

The tokens are passed by reference only, to `secret-run`, never by value.
Put the references in `testing/machines/.env`, which git ignores, so the public repository never names a vault:

```
ROBOT_USER_REF=op:Vault/Item/username
ROBOT_PASSWORD_REF=op:Vault/Item/password
HCLOUD_TOKEN_REF=op:Vault/Item/token
```

The Robot user is a web service user, made in Robot under *Settings, Web service and app settings*, with ordering enabled.
The first order uploads `~/.ssh/id_ed25519.pub` to Robot's key store, since an order names keys by fingerprint.

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
it installs Xorg, i3, Mesa and botropolis's libraries with apt,
forces a 1920x1080 display on with an EDID from `edid.py` through the DRM debugfs `edid_override`, since the kernel command line cannot change without a reboot,
and starts Xorg with the `modesetting` driver on the iGPU, i3, `xset s off -dpms` and no locker.
It writes what it found in `/dev/dri`, the Mesa version and the renderer to `dri.txt` in the results, and stops if there is no iGPU, since Hetzner may not leave it enabled.
`machine.txt` names the rescue system's Mesa version, since it is Debian's and not the one on Aria's laptop.
A failed set-up cancels the box like any other failure.

The soak runs on a synthetic history of 200 sessions in 150 projects, made by `botropolis-demo synth-home` ([item 248](../../roadmap/248-a-synthetic-history-cannot-be-made-outside-go-test.md)).
Nothing from a real `~/.claude` goes to a rented machine: the runner refuses one.

The soak box is ordered without the paid IPv4 address.
This was decided on a machine whose IPv6 came over a mobile link (`wwan0`); on a network without IPv6, add `IPV4=1`.

## The Wayland machine

The VM is Fedora 42 (GNOME 48, Plasma 6), turned into a desktop by `cloud/cloud-init.yaml.tftpl`:
the desktop logs `tester` in automatically, never locks, and runs `ydotool`, so keys go in below the compositor.
`SCRIPT` runs as `tester` inside that session, with `RESULTS` naming the directory that comes back.

## Checking it without an account

`make test` at the root checks the runner against stubs and a fake Hetzner, formats the Terraform, and shellchecks the set-up.
It validates the Terraform only when the hcloud provider is already cached, and says so when it is not.
`make validate` here caches it, which needs the network but no account.
