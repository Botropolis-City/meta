---
name: roadmap-start
description: >-
  Start work on a numbered botropolis roadmap item in its own background Claude
  Code session and git worktree. Use when asked to start, kick off, pick up,
  launch or hand off a roadmap item, or to release one that stopped. Checks the
  item is open, unclaimed, nobody's call and not waiting on another item, claims
  it on its status line, launches a session named "item NNN" in a worktree of
  the repository the work lands in, and hands it the workflow.
---

# Start a roadmap item

Run it from the meta repository's root, `~/workspaces/github/botropolis-city`.
One item, one session, one worktree: agents work beside each other on their own branches and land straight on `main`, so nobody edits a tree another agent is building in.

## 1. Check the roadmap

```sh
git pull --rebase github main
make docs-check
```

If the check fails, stop and report it: a claim written onto a roadmap that does not hold is the wrong first commit.

## 2. Check the item can start

Read `roadmap/NNN-*.md` and its row in `ROADMAP.md`'s open table.

- **Open.** Line 3 starts `**Open`. Anything else, stop.
- **Unclaimed.** Line 3 does not say `in progress since`. If it does, report the session it names and whether that session is alive (`claude agents`); a claim whose session is gone is stale, and taking it over is Aria's call, so ask.
- **Not waiting on another item.** For each entry on its `Depends on:` line: `N` needs item N closed; `N (slice K)` needs item N closed or carrying a `Landed: slice K` line. If either is missing, stop and name what it waits on.
- **Nobody's call.** If the open table's *whose call* cell starts with `Aria`, it needs Aria's decision first: stop and name the decision. A cell with `until` in it is parked; ask before starting it.
- **A vision item** (its file has a `Details:` line) needs `vision/` checked out here, with its details at the path that line names. Without them, stop: the session would start without knowing what to build.

## 3. Choose where the work lands

The repository the item's code lives in: `botropolis` for the app, `botropolis.city` for the website.
The item usually says, by naming files; if it touches both, start it where most of the work is and say so in the report.
Roadmap-only work is not started this way; the roadmap session does it.

That directory must be **trusted** by Claude Code, or a background session refuses to start there, and trust is not inherited from the meta root.
After the repositories moved on 2026-10-15, none of the three children was trusted yet.
Check before claiming, so a refusal does not cost a claim and a release in public history:

```sh
jq -r --arg p "$PWD/botropolis" '.projects[$p].hasTrustDialogAccepted // false' ~/.claude.json
```

If it prints anything but `true`, stop and ask Aria to run `claude` in that directory once and accept the prompt.
Never edit `~/.claude.json` to trust a directory: trusting one is Aria's decision, and live sessions rewrite that file.

## 4. Claim it

Rewrite line 3 so it starts with the claim, keeping everything after `Open.`:

```markdown
**Open, in progress since 2026-10-16 in the session "item 85". Filed 2026-10-16 (r412), a vision item: its details are private. Nobody's call.**
```

The shape is fixed, because `make docs-check` and the status line both read it: `Open, in progress since YYYY-MM-DD in the session "<name>". `, then the rest of the line.

```sh
make docs-check
git add roadmap/NNN-*.md
git commit -m "Start item NNN: <title, or a vision item's public name>"
git pull --rebase github main && git push github main
```

If the rebase stops on line 3 of the item, another session claimed it first: `git rebase --abort`, `git reset --hard github/main`, and report who has it.

## 5. Launch it

```sh
cd <repository>
claude --bg -w item-NNN -n "item NNN" --add-dir ~/workspaces/github/botropolis-city "<the kickoff prompt>"
```

- `-w item-NNN` makes the worktree `<repository>/.claude/worktrees/item-NNN` on the branch `worktree-item-NNN`, from `main`.
- `-n "item NNN"` is the name the claim records; `claude agents`, the city and the status line all show it.
- `--add-dir` gives the session the roadmap, the roadmap skills and, for a vision item, `vision/`.
- The session runs in Aria's default permission mode; nothing here changes it.

It prints `backgrounded · <id> · item NNN`.
Report the id and `claude attach <id>`.
If it refuses to start, release the claim (below) and report what it said.

## 6. The kickoff prompt

Fill in the braces and send the rest as written: every worker starts cold, so this is the whole hand-off.
Leave out the two lines marked *vision* for a normal item.

```text
Work roadmap item {N}, "{title or public name}". This worktree is yours alone: other agents work in their own, beside you, and everyone lands on main.

The roadmap and its skills are in {meta root}, which this session can read and write; the code is this worktree of {repository}.

1. Read the item, {meta root}/roadmap/{file}, and everything it links to.
   (vision) Its details are private: read {meta root}/vision/items/{file}, and the vision documents it links to.
2. Start from the latest main: git fetch github && git rebase github/main.
3. Work the way the CLAUDE.md files say: test first, red then green. Before writing a test file, show Aria the test tree and wait for an answer, unless the item records a tree Aria agreed.
4. Land each slice as soon as its tests pass: git fetch github && git rebase github/main, run make lint and the tests again, then git push github HEAD:main. Every commit cites "item {N}" and is signed; check with git verify-commit HEAD. Run make publishable before any push that adds an image.
5. When a slice lands, add "Landed: slice K (`<sha>`, r<N>)." under the item's Depends on line in {meta root}, then commit and push it there. Items waiting on that slice read that line.
   (vision) This is a vision item: never quote its details, the vision documents or the reasoning behind them in anything public — commits, code comments, docs, frames, the changelog. Say what the code does and cite the item number; the details stay private after it ships.
6. When everything the item asks for has landed, close it with the roadmap-close skill, from {meta root}. If you stop before that, release it with the Release steps in the roadmap-start skill, so it is not left claimed.
```

## Release

When a session stops before its item is done, or Aria takes an item back:

1. Make sure every slice that landed has its `Landed:` line.
2. Rewrite line 3 back to `**Open. Filed …**`, dropping the claim and nothing else.
3. `make docs-check`, commit `Release item NNN: <title or public name>`, then pull with rebase and push.
4. `claude stop <id>` if the session is still running; its conversation is kept, and `claude respawn <id>` brings it back.

The worktree stays until Claude Code's sweep removes it, once it holds nothing unpushed and is older than `cleanupPeriodDays`.
To remove one sooner, after its session has stopped: `git -C <repository> worktree remove .claude/worktrees/item-NNN`, which refuses while anything in it is uncommitted. Never pass `--force`.

## Report

The item, the session's id and name, where its worktree is, and how to attach.
If it could not start, say which check stopped it and what would clear it.
