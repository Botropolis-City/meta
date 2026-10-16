---
name: roadmap-close
description: >-
  Close a numbered botropolis roadmap item as Done or Fixed once its work has
  landed, or adjudicate it closed with a reason. Use after finishing an item's
  work, or when asked to close, mark done or resolve a roadmap item. Updates
  the item's status line with the date, commit and revision, removes every
  link to it from ROADMAP.md, runs make docs-check, and commits to main.
---

# Close a roadmap item

Run it from the meta repository's root, `~/workspaces/github/botropolis-city`.

## 1. Confirm it is done

Read the item and check what it asked for against what landed: the commit, the tests, the frame.
If only part landed, do not close it: leave it **Open**, and record each slice that landed under its `Depends on:` line (or line 5, if it has none) as `Landed: slice K (`<sha>`, r<N>).` — items that wait on a slice read that line, so it is not free text.
If it is closed by a decision rather than a fix, the reason goes in the body. "Not doing", with why, is a valid close.

## 2. Rewrite the status line

Line 3 of `roadmap/NNN-*.md`. Keep the filing history:

```markdown
**Done 2026-10-11 (`abc1234`, r380). Filed 2026-10-10 (r376) at Aria's request.**
```

- `Done` for work and requests, `Fixed` for defects. The checker treats anything not starting with "Open" as closed.
- The commit is the one that did the work, not this one, and it lives in the child it landed in; its revision is `git -C botropolis rev-list --count <sha>` (or `-C botropolis.city` for the website).
- Add a short closing section to the body: what was done, the frame or test that shows it, and any deviation from what the item asked, flagged for Aria.
- **A vision item** (its file has a `Details:` line) closes on its status line alone, which already carries the commit and revision: no closing section, because its stub may hold nothing else and `make docs-check` fails one that does. The details and the reasoning stay private after it ships; anything worth recording about how it landed goes in its details file in `vision/items/`, committed there.
- A claim (`Open, in progress since … in the session "…". `) goes with the rewrite: the Done line starts with `Done`.

## 3. Unlist it everywhere

`make docs-check` treats **any** link to the item in `ROADMAP.md` as listing it as open, so remove all of them:

```sh
grep -n 'roadmap/NNN-' ROADMAP.md
```

That catches the open table row and any `## Waiting on Aria` bullet.
Other items may name it on their `Depends on:` line, and their rows show it; leave both as they are: a closed dependency counts as met, and the line stays a record of what waited on what.

## 4. Check, commit, push

```sh
make docs-check
git add ROADMAP.md roadmap/NNN-*.md
git commit               # "Close item NNN: <title>"
git pull --rebase github main && git push github main
```

For a vision item, the subject uses its public name, `Close item NNN: <public name>`, and the body names only the commit and revision that closed it.
Anything more goes in its details file and the vision repository's commit, both private.

If it was worked in a worktree by `roadmap-start`, its session can stop now, and `roadmap-start`'s *Tidy* step removes the worktree, keeping the transcript.

## Report

Name the item, what closed it, and anything left for Aria to look at, such as a frame to judge.
