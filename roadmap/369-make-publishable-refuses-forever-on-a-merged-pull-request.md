# 369. `make publishable` refuses forever on a merged pull request's ref

**Fixed 2026-11-07 (`599b4ee9`, r1344). Filed 2026-11-07 (r1343), from the roadmap manager's pushes. Nobody's call — a defect in a guard.**

Landed: slice 1 (`e84dc9d`, r1343).

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

## Closed

Both guards sweep instead of refusing: meta's in `b8cc546` and `e84dc9d`, botropolis's in `599b4ee9` (r1344), with a test-only follow-up in `4aa474ce` (r1345).
A `refs/pull/*` ref outside the history, or a branch at the same commit as one, is fetched without leaving a local ref, and the commits it adds are swept for tokens in both blobs and messages.
Clean, it passes and the summary names it; with no tokens list it passes and the summary says it went unswept.
Any other branch, and every tag, still fails.

The tests are `testing/acceptance/publishable_test.py` here and `testing/acceptance/publishable_test.go` in botropolis: a clean pull request passes and is named, a token in a file or a commit message fails, no tokens list says it went unswept, an open pull request's branch passes, and any other branch fails.
Seven mutations went red in each guard: no exemption, an exemption without the sweep, an exemption for every ref, no fetch, a sweep of `--all` instead of what the ref adds, and the branch match set to never and to always.
botropolis's fixture at first let the no-fetch mutation pass, because a local `git clone` copies every object in the remote; it now clones with `--no-local`.

For Aria: this machine has no `.publishable-tokens`, so here every pull ref reads "NOT swept"; the sweep runs for real only where the list is.
