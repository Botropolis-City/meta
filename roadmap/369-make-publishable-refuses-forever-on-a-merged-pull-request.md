# 369. `make publishable` refuses forever on a merged pull request's ref

**Open, in progress since 2026-11-07 in the session "item 369". Filed 2026-11-07 (r1343), from the roadmap manager's pushes. Nobody's call — a defect in a guard.**

On 2026-11-07 a pull request was squash-merged into `main` in meta, botropolis and botropolis.city, each the first in its repository, at Aria's direction.
Its branch is deleted, but GitHub keeps `refs/pull/N/head` for good, and a squash merge leaves that commit outside `main`'s history.
So `make publishable` refuses every push in all three repositories with *"refs/pull/1/head (…) is not in the history being published"*.
It cannot pass again, and a guard that always refuses gets bypassed, which is the silent fallback again.

## Where it stands

`tools/check-publishable` here, and botropolis's own, check each advertised ref with `git merge-base --is-ancestor <sha> HEAD` (step 2, around line 91).
That rule is right for branches and tags: a ref outside the history being published holds something the sweep never read.
A `refs/pull/*` ref is the same risk, since its content is public, but it can never be made an ancestor.

## The fix

Read the content rather than the ancestry. For a `refs/pull/*` ref outside `HEAD`'s history, fetch it and run step 1's sweep over the commits it adds, then pass the ref if they are clean, and say so by name in the summary.
Keep refusing branches and tags outside the history, as now.
Test it in both repositories' guard tests: a merged pull request's ref with clean commits passes and is named; one with a token in its commits fails; a branch outside the history still fails.
Mutate each red, as the guard's history asks ([CLAUDE.md](../CLAUDE.md), "The documentation guard").
botropolis.city has its own `publishable`, so check whether it shares the same check.
