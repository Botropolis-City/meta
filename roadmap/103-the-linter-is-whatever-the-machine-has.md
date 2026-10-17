# 103. The linter is whatever version the machine happens to have

**Open, in progress since 2026-10-17 in the session "item 103". Filed 2026-10-17 (r552) at Aria's request. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`1044121`, r557).

`make lint` runs `golangci-lint` from `PATH` (`botropolis/Makefile`, the `lint` target), so its version is whatever the system package manager last installed.
On 2026-10-17 a system update moved this machine to golangci-lint 2.15.0, and its errcheck failed `make lint` on main for every item session, on a receive in `pkg/daemon/watch.go` unchanged since September.
Item 89 fixed that line (`127e828`, r549), and `make lint` is green again, but nothing stops the next update doing the same.

CI pins its own: `botropolis/.github/workflows/ci.yml` installs golangci-lint v2.13.2 and Go 1.27.1, with a comment saying the two must move together because an older linter cannot read a newer Go's export data.
So locally and in CI the code is linted by different versions, and a lint result here says nothing about CI's.

Aria, 2026-10-17: *"We should run a pinned version in the repo as a dependency if possible. But either way, we need to get linting working again."*

## The fix

Pin golangci-lint in the repository, so `make lint` and CI run the same version on every machine: Go's `tool` directive in `go.mod` (`go get -tool`, run as `go tool golangci-lint`) is the first candidate, since it versions the linter with the module and needs nothing installed.
golangci-lint's own documentation advises against building it from source this way, because its dependencies then resolve against the module's; if that bites, a separate `tools` module, or a pinned version checked by `make lint` against the installed one, are the fallbacks.
Whichever is chosen, CI's step uses the same pin, the Go version moves with it as the CI comment asks, and `make lint` stays green on main.
Nothing is installed on the system outside its package manager.

Tests: `make lint` green on main with the pinned version; and a check — in `make lint` or an acceptance test — that fails when the version run differs from the pin, mutated red once before it is trusted.

## Answered while building

- **What is pinned, and where** (Aria, 2026-10-17): *"We should pin both versions in our go.mod and make should use that regardless of what pacman has installed."* So go.mod carries a `toolchain` line and golangci-lint as a `tool` directive; the Makefile runs that exact Go through `GOTOOLCHAIN`, since `auto` would prefer a newer local Go; and CI reads both from go.mod. If the linter's dependencies would move any of the app's own, that comes back to Aria before landing.
- **Not in the app's own go.mod after all** (item 103's session, 2026-10-17): adding golangci-lint there moved 24 of the app's dependencies, 15 of them compiled into the binaries, so every linter bump would quietly move what the app ships.
- **Go's best practice, then** (Aria, 2026-10-17: *"Let's do whatever go best practices is. Research that"*): golangci-lint's install docs recommend a binary, and for `go tool` users a dedicated module or module file, since a tool's dependencies otherwise change the project's and its own `replace` directives do not apply; Go's toolchain docs make the `toolchain` line a preference a newer local Go overrides, and only an exact `GOTOOLCHAIN` forces it. So the linter is pinned in `tools/lint/go.mod`, with any `replace` directives of its own copied there; the app's go.mod carries `toolchain go1.27.2`; the Makefile exports `GOTOOLCHAIN` from that line; and CI reads both. mise, the other route the docs name, was left out because every contributor would need it installed.
- **The AUR package** (manager, 2026-10-17): unchanged; it calls `go build` directly and builds with pacman's Go while that is at least the pin. Setting `GOTOOLCHAIN=local` in its `build()` is a packaging call for later.
- **The test tree** (manager, 2026-10-17): `TestToolchainPins` in `testing/acceptance/toolchain_pin_test.go`, approved as proposed — a decoy linter first on `PATH` passes, a different linter or Go fails naming both versions — each check mutated red once.
