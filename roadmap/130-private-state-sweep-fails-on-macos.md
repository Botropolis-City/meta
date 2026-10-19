# 130. The private-state sweep's test fails on macOS, and CI is red

**Fixed 2026-10-19 (`5415e20`, r673; `9cf3655`, r672). Filed 2026-10-18 (r667), from what item 129 found. Nobody's call — a defect.**

Landed: slice 1 (`5415e20`, r673).
Landed: slice 2 (`5415e20`, r673).
Landed: slice 3 (`9cf3655`, r672).

`TestMakePrivateSweeps` fails on both macOS runners (`botropolis/pkg/statedir/statedir_test.go:188`, "when a private directory's pid now belongs to another process / it should remove it"), and `ci` on main has been red for three runs since item 114's slice 4 landed (`e6c8539`, r638).
Item 114's sweep tells a live owner from a reused pid by the process's start time, read from `/proc/<pid>/stat`, which macOS does not have; there the start time cannot be read, so a reused pid looks like a live owner and its directory is kept.

## The fix

Read a process's start time on macOS too (`sysctl` `kern.proc.pid`, whose `kp_proc.p_starttime` is the same fact), behind the one function the sweep already calls, so the rule is the same on both systems; failing that, say plainly what macOS does instead and make its test say so rather than skip silently.

Done when `ci` on main is green on every runner, macOS included, three runs in a row.

## Answered while building

- **Three failures, one item** (item 130's session, 2026-10-18; manager's ruling): besides the sweep, `botropolis-demo stage` read start times from `/proc` too and has refused to run on a Mac since item 124's first slice (r659), and item 124's daemon test built a socket path longer than macOS allows. All three keep `ci` red on macOS, so all three are fixed here: one `pkg/proc` reads a process's start time on Linux and on macOS for both callers, unstage takes it as a function, and the test's two lines swap.

## Two more macOS failures, in the same fix (2026-10-18)

By r667 the macOS jobs failed three tests, not one, and Ubuntu passed all three.
`botropolis-demo`'s `TestRun` failed for the same reason as the sweep: item 124's slice 1 (`e2037b2`, r659) made `pkg/demo`'s stand-ins read their start time from a second copy of the `/proc` parser, and `Sleepers` refuses a stand-in with none.
**So `botropolis-demo stage` did not work on a Mac at all from r659 until this item's slice 1.**
`pkg/appd`'s `TestDaemonStart` (item 124's slice 2, `783c579`, r660) was a test bug: it set `TMPDIR` to `t.TempDir()` before making the socket's directory with `os.MkdirTemp("", ...)`, so the socket path ran past the 104 bytes macOS allows and `bind` failed.

The manager ruled all three in scope here, since the item is done only when every runner is green, in three slices:

- slice 1: `pkg/proc.StartTime(pid) (uint64, bool)`, from `/proc/<pid>/stat` on Linux and `sysctl` `kern.proc.pid` through `golang.org/x/sys/unix` on macOS, and false elsewhere; `statedir` and `demo` both call it, and their private parsers are deleted;
- slice 2: `demo`'s `unstage` takes a start-time function instead of a faked `/proc`;
- slice 3: `TestDaemonStart` makes the socket's directory before it moves `TMPDIR`.

macOS is proven only by CI, so the item closes after three consecutive `ci` runs on main that are green on every runner.

## Closed (2026-10-19)

`pkg/proc.StartTime` is now the one place that reads when a process started: `/proc/<pid>/stat` on Linux, `sysctl` `kern.proc.pid` on macOS, and nothing elsewhere.
`statedir`'s sweep and the demo's stand-ins both call it, and their two copies of the `/proc` parser are gone (`5415e20`, r673).
`TestDaemonStart` makes its socket's directory before it moves `TMPDIR` (`9cf3655`, r672).
`pkg/proc`'s `TestStartTime` runs on every runner, and `ci` on main was green on every runner, both macOS ones included, three runs in a row: 39205791635 (r673), 39225611785 and 39227516940.

Two deviations from the tree, both approved by the manager.
The child's case reads "it should not give an earlier time than this process's", because Linux counts in 10 ms ticks and a child can share its parent's tick.
`TestUnstage`'s "not yet become sleep" and "is a sleep" cases now have the same fixture, since the process name was all that told them apart and `unstage` stopped reading it in item 124; both were kept.

**Left for later:** `pkg/app`'s `groupAlive` still reads only `/proc`, so on macOS it waits out its limit rather than seeing the group exit.
That is safe but slower, and `pkg/proc` is the obvious place to fix it.
