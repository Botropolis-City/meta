# 316. make publishable fails in a worktree whenever the main checkout has not pulled the latest push

**Open, in progress since 2026-10-28 in the session "item 316". Filed 2026-10-28 (r1197), reported by item 314's session. Nobody's call — a defect in a guard.**

`tools/check-publishable` checks that every ref the remote advertises is an ancestor of `main` (`git merge-base --is-ancestor "${sha}" main`, about line 94).
A worktree shares the main checkout's local `main` branch, which only a `git pull` there moves; so once any session pushes, every worktree's `make publishable` fails on `refs/heads/main` until someone pulls the main checkout.
Item 314's session pushed its close beside that failure.
A guard that fails on every healthy run trains its callers to push past it, which is the worse defect.

## The fix

1. Compare against the remote's own `main` after a fetch (`github/main`), or against `HEAD` when `HEAD` contains it, never the local branch another checkout owns; keep the tag check that is the point of the guard (a ref not in main's history still fails).
2. Do the same in botropolis's `make publishable` if it shares the fault.
3. Tests: a worktree whose local `main` is behind the remote passes; a remote tag outside main's history still fails, mutated red.
