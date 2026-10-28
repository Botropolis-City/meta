# 316. make publishable fails in a worktree whenever the main checkout has not pulled the latest push

**Fixed 2026-10-28 (`cbea0c1`, r1166 of meta). Filed 2026-10-28 (r1197), reported by item 314's session. Nobody's call — a defect in a guard.**

`tools/check-publishable` checks that every ref the remote advertises is an ancestor of `main` (`git merge-base --is-ancestor "${sha}" main`, about line 94).
A worktree shares the main checkout's local `main` branch, which only a `git pull` there moves; so once any session pushes, every worktree's `make publishable` fails on `refs/heads/main` until someone pulls the main checkout.
Item 314's session pushed its close beside that failure.
A guard that fails on every healthy run trains its callers to push past it, which is the worse defect.

## The fix

1. Compare against the remote's own `main` after a fetch (`github/main`), or against `HEAD` when `HEAD` contains it, never the local branch another checkout owns; keep the tag check that is the point of the guard (a ref not in main's history still fails).
2. Do the same in botropolis's `make publishable` if it shares the fault.
3. Tests: a worktree whose local `main` is behind the remote passes; a remote tag outside main's history still fails, mutated red.

## What landed

`tools/check-publishable` now measures every advertised ref against `HEAD`, the history being published, as botropolis's check already did (`cbea0c1`).
`HEAD` rather than `github/main` because a worktree lands with `push HEAD:main`, and after a rebase onto `github/main` it contains it; one not yet rebased still fails, as its push would be refused anyway.
botropolis needed nothing: its check has measured against `HEAD` since before this item, for this same reason.

`testing/acceptance/publishable_test.py`, run by `make test`, builds throwaway repositories in a temp directory: a bare remote, a main clone, a second clone that lands, and a worktree.
A worktree whose local `main` is behind the remote passes (red before the fix, on `refs/heads/main` and `HEAD`), and so does an up-to-date main clone, a case the manager added.
A remote tag outside the published history fails and is named, and a remote `main` ahead of an unrebased `HEAD` fails; making the ancestor check always pass turned all three red.
This worktree's own `make publishable` passed with its main checkout behind, which is the case that failed before.
