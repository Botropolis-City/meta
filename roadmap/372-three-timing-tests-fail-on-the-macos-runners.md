# 372. Three timing tests fail now and then on GitHub's macOS runners

**Open. Filed 2026-11-07 (r1343), split out of [item 355](355-the-landing-queue-s-slow-waiter-test-times-out-on-macos-intel.md)'s "Seen since". Nobody's call — flaky tests.**

Item 355's own failure turned out to be a defect in the landing queue, not the runner. These three were listed beside it, but have different packages and causes:

- `pkg/daemon` `TestRequestRescan`, *"when the watcher has just rescanned and a background pass asks for another"*, on `macos-26-intel`, run 42265186145;
- `pkg/measure` `TestThread`, *"it should count at least 80% of the CPU the process spent"*, on `macos-26-intel`, run 42284185651;
- `TestWatch`, *"when a subagent transcript appears under a live session"*, on `macos-26`, in the same run.

Each passed on a rerun and on Linux.

## The fix

Take each on its own terms, as 355 did: reproduce it, by stretching the window it depends on on Linux if the runner can't be had, and say whether it is the test or the code.
Then fix the cause, never the bound alone. A bound may be widened only where it was taken from the runner's speed rather than from what the case needs, and the item says which.
