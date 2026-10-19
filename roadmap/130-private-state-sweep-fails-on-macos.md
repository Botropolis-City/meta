# 130. The private-state sweep's test fails on macOS, and CI is red

**Open, in progress since 2026-10-18 in the session "item 130". Filed 2026-10-18 (r667), from what item 129 found. Nobody's call — a defect.**

`TestMakePrivateSweeps` fails on both macOS runners (`botropolis/pkg/statedir/statedir_test.go:188`, "when a private directory's pid now belongs to another process / it should remove it"), and `ci` on main has been red for three runs since item 114's slice 4 landed (`e6c8539`, r638).
Item 114's sweep tells a live owner from a reused pid by the process's start time, read from `/proc/<pid>/stat`, which macOS does not have; there the start time cannot be read, so a reused pid looks like a live owner and its directory is kept.

## The fix

Read a process's start time on macOS too (`sysctl` `kern.proc.pid`, whose `kp_proc.p_starttime` is the same fact), behind the one function the sweep already calls, so the rule is the same on both systems; failing that, say plainly what macOS does instead and make its test say so rather than skip silently.

Done when `ci` on main is green on every runner, macOS included, three runs in a row.

## Answered while building

- **Three failures, one item** (item 130's session, 2026-10-18; manager's ruling): besides the sweep, `botropolis-demo stage` read start times from `/proc` too and has refused to run on a Mac since item 124's first slice (r659), and item 124's daemon test built a socket path longer than macOS allows. All three keep `ci` red on macOS, so all three are fixed here: one `pkg/proc` reads a process's start time on Linux and on macOS for both callers, unstage takes it as a function, and the test's two lines swap.
