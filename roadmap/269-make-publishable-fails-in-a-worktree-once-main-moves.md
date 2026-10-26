# 269. `make publishable` fails in an item worktree once github's main moves past the shared checkout's

**Open. Filed 2026-10-26 (r1096), from item 245's session. Nobody's call — a defect in a guard.**

`tools/check-publishable` checks every ref GitHub advertises against main's history, at line 94:

```sh
if ! git merge-base --is-ancestor "${sha}" main 2>/dev/null; then
    note "${ref} (${sha:0:10}) is not in main's history"
```

`main` there is the **local** branch.
In an item worktree that is the shared checkout's `main`, which lags `github/main` until someone pulls in it, so once any session pushes, every other worktree's `make publishable` fails "refs/heads/main (…) is not in main's history" although everything is pushed and clean.
Item 245's session saw it on 2026-10-26: it passed for a code push and failed, minutes later, for a one-line `Landed:` push, with `make docs-check` green.

The check's purpose is that nothing GitHub serves lies outside the history being published; the history being published is `HEAD`, which after `git rebase github/main` contains `github/main`.

## The fix

Test each advertised ref against `HEAD` (falling back to `main` only outside a checkout's branch, and saying so, as the guard does for its other fallbacks).
Tests: in a worktree whose local `main` lags `github/main`, with `HEAD` rebased onto `github/main`, the check passes; a ref advertised that is in neither still fails; and mutated back to `main`, the first case goes red.
Check botropolis's `tools/check-publishable` for the same line and fix both.

A guard that fails on a clean tree teaches people to push past it, which item 245's session then did once; that is the cost of leaving it.
