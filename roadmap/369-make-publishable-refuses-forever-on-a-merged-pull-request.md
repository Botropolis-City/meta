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

## Answered while building

- **The design and test tree** (roadmap manager, 2026-11-07): approved, the same in both guards. A `refs/pull/*` ref outside the history is fetched without leaving a local ref, then swept over `<sha> ^HEAD`, both blobs and messages. If clean it passes and is named; a token or a failed fetch fails it, naming it.
  With no tokens list, it passes but says it went unswept.
  Branches and tags outside the history still fail.
  Four mutations each go red.
- **botropolis.city has no guard at all**: filed as its own item, which follows this one.
- **A pull request's branch is swept too** (roadmap manager, 2026-11-07). A rule added to CLAUDE.md the same evening (*"Workspace bots land through pull requests"*) means a remote often holds an open pull request's branch, and every push meanwhile was refused, the same always-refuses problem, only sometimes.
  So a branch that some `refs/pull/*/head` points at is swept like that ref, not refused. Any other branch outside the history still fails.
  That gets its own test and mutation in both guards.
