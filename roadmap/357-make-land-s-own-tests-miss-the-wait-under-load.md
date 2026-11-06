# 357. `make land`'s own acceptance tests miss the wait under load

**Open. Filed 2026-11-06 (r1270), from items 343's and 350's sessions landing at a load of about 40. Nobody's call — a flaky test.**

Three acceptance tests of the landing lock failed in the gate of two different sessions on 2026-11-06, each with the same assertion:
`TestLand` *"when two sessions run make land at once"* (`testing/acceptance/land_test.go:243`), `TestAcceptanceLocked`, and `TestDemoMediaLocked` *"when another session holds the landing lock"* (`:657`).
Each expects the second command's output to contain *"Waiting for the landing in progress"*, and it did not.
All three passed when run alone.

## Why

Under load, the first landing in each test finishes before the second command looks for the lock, so the second never waits and never prints the line.
The tests time the two commands against each other, and the machine's speed decides the outcome.

## The fix

Hold the first command inside the lock until the second has been seen waiting — a fake gate that blocks on a file the test releases — so the order is forced rather than raced, and assert on the line after that.
`land_test.go:436` and `:530` assert the same line and want the same check.
