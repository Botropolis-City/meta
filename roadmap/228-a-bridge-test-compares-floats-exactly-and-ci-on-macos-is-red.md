# 228. A bridge test compares floats exactly, so CI on macOS has been red since item 217

**Open. Filed 2026-10-24 (r969), from the botropolis status line's "ci red a555de7". Nobody's call — a defect in a test.**

CI on `main` has failed on every push since item 217's first slice (`08:05` UTC, run 40076680239), and again at runs 40079304155 and 40081230765.
Only `test-macos (macos-26)` fails, in `make test-unit`:

```text
--- FAIL: TestPullRequests/when_the_island_grows_a_row_while_a_truck_is_on_its_way,_so_the_bridge_moves/and_the_truck_is_already_on_the_deck/it_should_carry_on_along_the_deck_as_it_now_stands,_as_far_out_as_it_was
    pkg/city/pullrequests_test.go:310
    expected: []city.Point{city.Point{X:23.199999988390566, Y:504}, city.Point{X:-273.6, Y:504}}
    actual  : []city.Point{city.Point{X:23.199999988390573, Y:504}, city.Point{X:-273.6, Y:504}}
```

**The mechanism.** The test, from [item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md), asserts the truck's path with `assert.Equal` on float points.
The two values differ in the last bits, most likely because the Go compiler fuses multiply-adds into one instruction on arm64 and not on amd64, so the same expression rounds differently on the macOS runner than on Linux.
The rest of `pkg/city`'s tests already compare floats with `assert.InDelta(…, 1e-9)` (`bridge_test.go`, `camera_test.go`); this one does not.

**The fix.** Compare the path point by point within `1e-9`, as the package's other tests do: its length exactly, then each point's X and Y.
Search `pkg/city`'s tests for other `assert.Equal`s on computed `city.Point`s and fix any in the same commit.
Mutate it red once: a point moved by more than the tolerance must still fail.

**A wrong premise this corrects.** [Item 226](226-the-acceptance-suite-takes-sixteen-minutes-to-land.md) says `make land` refuses to land while `main` is red.
It does not: `tools/ci-status`, from item 202, reports and never gates, so that a red `main` cannot stop the landing that fixes it.
This is how three landings went out on a red `main` without anyone being stopped.
