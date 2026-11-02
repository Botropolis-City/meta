# 332. The landing queue's tests run under no make target, so nothing runs them

**Open. Filed 2026-11-03 (r1233), noticed by item 330. Nobody's call — a guard not invoked.**

`botropolis/tools/land-queue` has tests (item 295's, and item 326's `inherit_linux_test.go`), and no `make` target runs them: `make test` covers the packages and the acceptance tree, not `tools/`.
A test nobody runs cannot fail, which is the rule the docs guard was built on.

## The fix

`make test-unit` (or a `test-tools` target `make test` depends on) runs `go test ./tools/...`, and a check that every Go test file under `tools/` is covered by a target `make test` reaches, mutated red by removing the target.
