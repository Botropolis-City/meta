# 263. The package's check reads the builder's own config, so 0.3.1 fails to build for anyone who set district_type

**Open, in progress since 2026-10-26 in the session "item 263". Filed 2026-10-26 (r1093), from Aria's install of 0.3.1 on another laptop. Nobody's call — a defect.**

Aria, 2026-10-26, installing `botropolis` 0.3.1 from the AUR over 0.2.2: the PKGBUILD's `check()` runs `go test ./cmd/... ./pkg/...`, and one test failed, so the package never built.

```
--- FAIL: TestDistrictTypeKey/when_district_type_is_not_set/it_should_be_random (0.00s)
    config_test.go:574: expected: "random"  actual  : "guess"
FAIL    botropolis.city/botropolis/pkg/config
```

## Why

`TestDistrictTypeKey` in `pkg/config/config_test.go` calls `load(t)` with nothing isolated.
`config.NewViper` reads `$XDG_CONFIG_HOME/botropolis/config.toml` (or `~/.config/botropolis/config.toml`) and, through `AutomaticEnv`, every `BOTROPOLIS_*` variable.
So the test asserts the default against whatever the building user configured, and a user who set `district_type = "guess"` cannot build the package.
`TestConfig`'s "when nothing is set" case already isolates `HOME`, `XDG_CONFIG_HOME` and the `BOTROPOLIS_*` variables; this test does not.
CI never sees it because its runners have no config.

The rule it breaks is the testing rule in the `CLAUDE.md` files: tests are idempotent and rely on no outside state.
The PKGBUILD's own comment already says a package build must not read the builder's `~/.claude`, and the same holds for their config.

## The fix

1. Isolate every test in `pkg/config` that loads a config: one helper that sets `HOME`, `XDG_CONFIG_HOME` to `t.TempDir()` and clears every `BOTROPOLIS_*` variable the package binds, used by `load` itself, so a new test cannot forget it.
2. Sweep the other packages `check()` runs for tests that read the real config or environment the same way, and isolate them too.
3. A guard that fails red before the fix: run the unit suite with a hostile config (a `config.toml` setting every key to a non-default value, and the matching `BOTROPOLIS_*` variables), as a make target that CI runs, so the next such test fails in CI, not on a user's machine.
4. Release it as 0.3.2's first fix, or as a 0.3.1 `pkgrel` bump of the AUR package whose `check()` sets `XDG_CONFIG_HOME` and `HOME` to a directory under `$srcdir`, whichever comes first.

Until then, `makepkg -si --nocheck` in the AUR checkout builds 0.3.1, and `botropolis-bin` does not run the tests at all.
