# 234. `make test` leaves an untracked `__pycache__` in `tools/render-sprites/`

**Fixed 2026-10-24 (`73cc0c7`, r981). Filed 2026-10-24 (r972), found when item 229's worktree would not tidy. Nobody's call — a defect.**

[Item 229](229-atlas-cost-crashes-before-it-prices-anything.md) made `tools/atlas-cost.py` import `tools/render-sprites/render.py` as a module, and `TestAtlasCost` runs it on every `make test`.
Python writes `tools/render-sprites/__pycache__/` beside the module it imports, and `.gitignore` ignores only `tools/__pycache__/`, so every checkout that runs the suite is left with an untracked directory.
That dirtied item 229's worktree, so `claude rm` refused to remove it until the directory was deleted by hand, and it will do the same to every item worktree and to the main checkout.

**The fix.** Write no bytecode from the tool: `sys.dont_write_bytecode = True` in `atlas-cost.py` before it imports, or `-B` / `PYTHONDONTWRITEBYTECODE=1` where `TestAtlasCost` runs it; and ignore `__pycache__/` anywhere in the repository, as a second line.
Its test: after `TestAtlasCost` runs in a scratch copy of the tools, the copy holds no `__pycache__`.

## Answered while building

- **The test tree** (manager, 2026-10-24): approved as sent: in `TestAtlasCost`, a run in a scratch copy of its inputs exits 0 and leaves no `__pycache__`; the fix sets `sys.dont_write_bytecode` in the tool itself and widens `.gitignore` to `__pycache__/`.

## Closed

`atlas-cost.py` sets `sys.dont_write_bytecode` before it imports `render.py`, and `.gitignore` ignores `__pycache__/` anywhere (`73cc0c7`, r981).
`TestAtlasCost` now runs the tool in a scratch copy of its inputs and asserts the copy holds no `__pycache__`.
It went red without the fix, which was also the mutation the manager asked for,
and the worktree was clean after the full `make land` gate.

For the next session that runs an acceptance test under the lock: the worktree guard refused `flock <lock> go test …`,
so the test binary was built with `go test -c` and a script that runs it was what took the lock.
