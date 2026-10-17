# 103. The linter is whatever version the machine happens to have

**Open, in progress since 2026-10-17 in the session "item 103". Filed 2026-10-17 (r552) at Aria's request. Nobody's call — a defect.**

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
