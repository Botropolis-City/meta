# 245. The tests that need another desktop or a whole night have no machine to run on

**Open, in progress since 2026-10-26 in the session "item 245". Filed 2026-10-25 (r1024) at Aria's request. Nobody's call — Aria chose the providers and where the code lives; the run waits on her Hetzner account.**

Depends on: nothing
Landed: slice 1 (`2b502b8`, r1032).

Aria, 2026-10-25, on how to test items 95 and 96 without owning a Mac or a Wayland desktop: *"I won't suddenly own one of these. We need a vm to test."*
And on item 164's overnight soak, which needs a screen that never blanks or locks: *"I meant remote vm like in linode or gcp or some other cloud env or maybe a cloud intended for perf or cross platform testing"*.

Three tests have nowhere to run:
- [item 164](164-no-soak-test-for-the-growth-budget.md)'s 8-hour soak (`performance/tools/perf-soak`, which takes `--display` and `--no-hide`) needs a visible X session that never locks, with a GPU on a Mesa driver so its GPU memory means what it does on Aria's laptop;
- [item 96](096-the-global-shortcut-on-wayland.md) needs GNOME 48 or later and KDE Plasma 6 Wayland sessions, with keys injected and screens captured;
- [item 95](095-the-global-shortcut-on-macos.md) needs macOS 14 or later with a GUI. It is not this item's: GitHub's hosted macOS runners serve it, from its own workflow.

## What Aria chose (2026-10-25)

- **The soak** runs on a **Hetzner EX44** dedicated server (Intel Core i5-13500, UHD 770 on Mesa's `iris`), billed by the hour with no setup fee, about €1 for a 10-hour run. Real Xorg with the `modesetting` driver on the iGPU and a forced EDID, i3, `xset s off -dpms` and no locker. Not VirtualGL, which copies each frame into the process's memory and changes what the soak measures; not Xvfb with llvmpipe, which hides GPU memory inside the process.
- **The Wayland desktops** run on a **Hetzner Cloud** VM, Fedora Workstation for GNOME and Fedora KDE for Plasma 6, each autologged into a normal session (KRdp has no headless mode). Keys go in over SSH through `ydotool` (uinput, below the compositor); screens come out through the screenshot portal or `spectacle -b`; the `BindShortcuts` confirmation dialog is accepted with keys.
- **The code lives in the meta repository, at `testing/machines/`**: `hcloud` Terraform for the cloud VM, and a reviewed script against Hetzner's Robot API for the EX44, which has no official Terraform provider. Nothing applies on push. A run is plan, Aria's approval, apply, test, destroy, and the destroy runs even when the test fails.
- **Secrets by reference only**: the Hetzner tokens come through `secret-run --env …=op:…`, never on a command line.

## The fix

1. `testing/machines/` with the Terraform, the Robot API script, the guest set-up (cloud-init or a script kept beside it), and a `Makefile` whose targets are `plan`, `apply`, `run-soak`, `run-wayland` and `destroy`, each saying what it will cost before it spends.
2. Tests that need no account: the Terraform validates and formats; the scripts' `--help` and their refusal to run without a token reference; a teardown that runs when the test step fails.
3. **Stop at the plan** until Aria has created the Hetzner account and named the token's 1Password reference; then `terraform plan` for her to read, and nothing applied without her.
4. Once applied once: check `/dev/dri` on the EX44 before the first soak, since Hetzner may not leave the iGPU enabled, and say what was found here.

Research, with sources, is in items 95 and 96's *Testing without the hardware* sections; prices are as found on 2026-10-25.
The machines, and how a run goes, are in [testing/machines](../testing/machines/README.md).

## Answered while building

- **The plan and tree** (manager, 2026-10-25): approved. One stdlib Python CLI and a Makefile in `testing/machines/`; a real EX44 order only after Aria types the hourly price back, and `terraform apply` without `-auto-approve`; destroy in a `finally` that runs on failure and on interrupt.
- **Network in `make test`** (manager): none. Terraform validates only against a provider already cached and says loudly when it skipped; `make validate` there fills the cache for a human.
- **The EX44's system** (manager): Arch, so its Mesa matches Aria's laptop and the GPU figure compares.
- **Whose sessions the soak replays** (manager, from the standing rule that nothing derived from `~/.claude` is copied): the demo's alone, and the report says so; nothing of Aria's history goes to a rented machine.
- **IPv4** (manager): IPv6-only by default, since this machine reaches IPv6 (over its mobile link), with `IPV4=1` adding Hetzner's paid address for a network without it.
- **Token references** (manager): Makefile variables with no default, set in a git-ignored `testing/machines/.env`, so nothing public names Aria's vault.
- **A history of real size** (manager, 2026-10-25, from a side agent's note to Aria): demo sessions alone would miss growth that scales with history, so the soak stages a synthetic home of at least 200 sessions in 150 projects, the size of Aria's, from the generator the cost tests use (`testing/helpers/fixtures.go`), with the demo's writers on top; its report names the counts and says the history was synthetic. A run on Aria's own machine with her real history stays possible before a release, with `--keep-awake` restored, if she asks for one.
- **Where the synthetic history comes from** (manager, 2026-10-25): `botropolis-demo synth-home`, filed as [item 248](248-a-synthetic-history-cannot-be-made-outside-go-test.md) since this item works only in the meta repository; `run-soak` takes a required `--history DIR`, refuses a path inside the real `~/.claude`, uploads it as the soak user's history under the demo's writers, and writes its counts into the report.
- **The account** (Aria, 2026-10-26): created, with a Hetzner Cloud project and its API token in 1Password; its reference is set in the git-ignored `testing/machines/.env` (no public file names the vault), and it resolves. The EX44 soak box is ordered through Hetzner Robot, which takes a separate web-service user and password, still to be created; until then only the Wayland VM can be planned.
- **What the soak box really costs** (manager, 2026-10-26, from Robot's ordering API on Aria's account, which charges no VAT): the EX44 is not orderable through the API at all, and every standard product with an integrated GPU carries a setup fee per order (AX42-1 €59 + €0.1877/h, EX63-1 €84 + €0.2758/h, so €61–87 a run), which the runner already refuses. The server auction lists used machines by the hour with no setup fee, among them a Core i5-12500 (Intel UHD 770 on `iris`, the EX44's own GPU) at €0.1763/h, about €1.76 for a ten-hour run.
- **The soak box** (Aria, 2026-10-26): the auction. The runner chooses, at order time, the cheapest auction server with an Intel integrated GPU and no setup fee, shows it and its price in the plan, and orders only after the price is typed back; it refuses anything with a setup fee or no hourly price.
