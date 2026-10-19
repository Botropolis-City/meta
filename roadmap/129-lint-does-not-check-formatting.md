# 129. Lint does not check that the Go is formatted

**Fixed 2026-10-18 (`c972571`, r662). Filed 2026-10-18 (r655), from what item 125 found. Nobody's call — a defect.**

Depends on: nothing

Landed: slice 1 (`9ca362f`, r658).

`gofmt -l` lists `pkg/render/reference.go` and `pkg/render/shore_test.go` on main, and `make lint` is green: `golangci-lint` runs without a formatting linter configured in `botropolis/.golangci.yml`, and nothing else in the `lint` target runs `gofmt`.
So unformatted code lands, and every later edit to those files carries an unrelated formatting diff.

## The fix

Make `make lint` fail on unformatted Go — the `gofmt` formatter in `.golangci.yml`, or a `gofmt -l` step in the target — format the two files, and say which in the item.

Tests: an unformatted file in a scratch copy of the tree makes `make lint` fail and name the file; mutated red on today's configuration.

## Closed

`make lint` fails on unformatted Go: `botropolis/.golangci.yml` enables golangci-lint's `gofmt` formatter, so the existing `golangci-lint run` step names the file, and no new Makefile step was needed (`c972571`, r662).
`testing/acceptance/format_test.go` runs `make lint` in a scratch copy of the tree with an unformatted file in `pkg/render`, and asserts it fails and names the file.
It was red on the previous configuration and is green on this one.
`make test` runs it, since nothing there passes `-short`, and so does CI's `make test lint`.

The two files were formatted first, as their own commit (`9ca362f`, r658), so item 127 could rebase onto them.

Flagged for Aria: the formatter simplifies, as `gofmt -s` does, which is golangci-lint's default, so it is stricter than the `gofmt -l` this item was filed from.
It found one more file that plain `gofmt` passes, `pkg/render/iso.go`, where an empty `var ()` had outlived its constants; that block and the comment above it were removed (`944e6e9`, r663).
