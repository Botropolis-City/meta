# Test machines

The machines for the tests that need another desktop or a whole night ([item 245](../../roadmap/245-test-machines-in-the-cloud.md)).
Each is rented from Hetzner by the hour, made for one run and destroyed after it.

| machine | what it is | for |
| --- | --- | --- |
| `soak` | a Hetzner EX44 dedicated server (UHD 770 on Mesa's `iris`), ordered through the Robot API | [item 164](../../roadmap/164-no-soak-test-for-the-growth-budget.md)'s 8-hour soak |
| `wayland` | a Hetzner Cloud VM running Fedora with GNOME or KDE Plasma 6 on Wayland, made by Terraform in `cloud/` | [item 96](../../roadmap/096-the-global-shortcut-on-wayland.md)'s global shortcut |

## A run

A run is plan, approval, apply, test, destroy, and the destroy runs when the test fails and when the run is interrupted.

```
make plan MACHINE=soak                   # the price, and a test order Hetzner does not process
make run-soak PERF_BUILD=dir             # order, set up, soak 8 hours, fetch the report, cancel
make plan MACHINE=wayland DESKTOP=kde    # the price, and terraform plan
make run-wayland DESKTOP=kde SCRIPT=file # make the VM, run SCRIPT in the session, fetch results, destroy
make destroy MACHINE=soak                # cancel by hand, if a run could not
```

Every target that spends says what it will cost first.
Nothing applies on its own, and nothing applies on push:
the EX44 is ordered only after the hourly price is typed back at the terminal,
and the VM only after Terraform's own `yes`.
The runner refuses an EX44 that is not billed by the hour or has a setup fee, because either would cost far more than a run.

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

`ex44/setup` turns the EX44's Arch into the soak's display:
real Xorg with the `modesetting` driver on the iGPU, a 1920x1080 display forced on with an EDID from `edid.py` through `drm.edid_firmware`, i3, `xset s off -dpms` and no locker.
It writes what it found in `/dev/dri` to `dri.txt` in the results, and stops if there is no iGPU, since Hetzner may not leave it enabled.

The soak runs on a synthetic history of 200 sessions in 150 projects, made by `botropolis-demo synth-home` ([item 248](../../roadmap/248-a-synthetic-history-cannot-be-made-outside-go-test.md)).
Nothing from a real `~/.claude` goes to a rented machine: the runner refuses one.

The EX44 is ordered without the paid IPv4 address.
This was decided on a machine whose IPv6 came over a mobile link (`wwan0`); on a network without IPv6, add `IPV4=1`.

## The Wayland machine

The VM is Fedora 42 (GNOME 48, Plasma 6), turned into a desktop by `cloud/cloud-init.yaml.tftpl`:
the desktop logs `tester` in automatically, never locks, and runs `ydotool`, so keys go in below the compositor.
`SCRIPT` runs as `tester` inside that session, with `RESULTS` naming the directory that comes back.

## Checking it without an account

`make test` at the root checks the runner against stubs and a fake Hetzner, formats the Terraform, and shellchecks the set-up.
It validates the Terraform only when the hcloud provider is already cached, and says so when it is not.
`make validate` here caches it, which needs the network but no account.
