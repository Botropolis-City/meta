# 234. `make test` leaves an untracked `__pycache__` in `tools/render-sprites/`

**Open, in progress since 2026-10-24 in the session "item 234". Filed 2026-10-24 (r972), found when item 229's worktree would not tidy. Nobody's call — a defect.**

[Item 229](229-atlas-cost-crashes-before-it-prices-anything.md) made `tools/atlas-cost.py` import `tools/render-sprites/render.py` as a module, and `TestAtlasCost` runs it on every `make test`.
Python writes `tools/render-sprites/__pycache__/` beside the module it imports, and `.gitignore` ignores only `tools/__pycache__/`, so every checkout that runs the suite is left with an untracked directory.
That dirtied item 229's worktree, so `claude rm` refused to remove it until the directory was deleted by hand, and it will do the same to every item worktree and to the main checkout.

**The fix.** Write no bytecode from the tool: `sys.dont_write_bytecode = True` in `atlas-cost.py` before it imports, or `-B` / `PYTHONDONTWRITEBYTECODE=1` where `TestAtlasCost` runs it; and ignore `__pycache__/` anywhere in the repository, as a second line.
Its test: after `TestAtlasCost` runs in a scratch copy of the tools, the copy holds no `__pycache__`.

## Answered while building

- **The test tree** (manager, 2026-10-24): approved as sent: in `TestAtlasCost`, a run in a scratch copy of its inputs exits 0 and leaves no `__pycache__`; the fix sets `sys.dont_write_bytecode` in the tool itself and widens `.gitignore` to `__pycache__/`.
