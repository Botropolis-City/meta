# 227. TestToolchainPins fails whenever the machine's Go is not the pin

**Open. Filed 2026-10-24 (r969), found by item 226's session during its slice 1. Nobody's call — a defect in a test.**

pacman has upgraded this machine's Go to 1.27.3, while `go.mod` pins `toolchain go1.27.2` ([item 103](103-the-linter-is-whatever-the-machine-has.md)).
`make go-version-check` still passes, since the Makefile exports `GOTOOLCHAIN` from the pin, but `TestToolchainPins` now fails on every landing on this machine.

**The mechanism.** In `botropolis/testing/acceptance/toolchain_pin_test.go`, the case *"and GOTOOLCHAIN is a different version"* writes a go.mod pinning a stale version and runs `make go-version-check GO_MOD=<it> GOTOOLCHAIN=local`.
With `GOTOOLCHAIN=local`, the Go that runs is the machine's own, but *"it should name the version that ran"* asserts the output contains `goPin`, the repository's pin.
That holds only while the machine's Go happens to be the pin, so the test depends on outside state, against the testing rules.

**The fix.** Assert that the output names the local Go's version, read with `GOTOOLCHAIN=local go env GOVERSION` in the case's setup, instead of `goPin`.
Mutate it red once: the assertion should fail if `tools/check-pin` stops printing the version that ran.
The stale version chosen for the scratch go.mod must also differ from the local Go's version, not only from the pin, or the check passes on a machine whose Go is that stale version.

Item 226's session fixes it, since it is in that item's landing path, and cites this item in the commit.
