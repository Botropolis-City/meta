# 129. Lint does not check that the Go is formatted

**Open, in progress since 2026-10-18 in the session "item 129". Filed 2026-10-18 (r655), from what item 125 found. Nobody's call — a defect.**

`gofmt -l` lists `pkg/render/reference.go` and `pkg/render/shore_test.go` on main, and `make lint` is green: `golangci-lint` runs without a formatting linter configured in `botropolis/.golangci.yml`, and nothing else in the `lint` target runs `gofmt`.
So unformatted code lands, and every later edit to those files carries an unrelated formatting diff.

## The fix

Make `make lint` fail on unformatted Go — the `gofmt` formatter in `.golangci.yml`, or a `gofmt -l` step in the target — format the two files, and say which in the item.

Tests: an unformatted file in a scratch copy of the tree makes `make lint` fail and name the file; mutated red on today's configuration.
