---
name: roadmap-start
description: >-
  Start work on a numbered botropolis roadmap item in its own background Claude
  Code session and git worktree. Use when asked to start, kick off, pick up,
  launch or hand off a roadmap item, or the next one when no number is given,
  or to release one that stopped. Checks the
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

## 2. Choose the item, if none was given

With no number, start the next ready one: the ready item the most open items wait on, then the lowest number.

```sh
python3 -c 'import sys; sys.path.insert(0, "tools"); import roadmap
items = roadmap.load(); print(roadmap.next_ready(items, roadmap.open_table(open("ROADMAP.md").read())))'
```

It prints `None` when nothing is ready: report what is claimed, blocked or waiting on Aria, as `roadmap-status` does, and stop.
Say which item was chosen and why before claiming it.

## 3. Check the item can start

Read `roadmap/NNN-*.md` and its row in `ROADMAP.md`'s open table.

- **Open.** Line 3 starts `**Open`. Anything else, stop.
- **Unclaimed.** Line 3 does not say `in progress since`. If it does, report the session it names and whether that session is alive (`claude agents`); a claim whose session is gone is stale, and taking it over is Aria's call, so ask.
- **Not waiting on another item.** For each entry on its `Depends on:` line: `N` needs item N closed; `N (slice K)` needs item N closed or carrying a `Landed: slice K` line. If either is missing, stop and name what it waits on.
- **Nobody's call.** If the open table's *whose call* cell starts with `Aria`, it needs Aria's decision first: stop and name the decision. A cell with `until` in it is parked; ask before starting it.
- **A vision item** (its file has a `Details:` line) needs `vision/` checked out here, with its details at the path that line names. Without them, stop: the session would start without knowing what to build.

## 4. Choose where the work lands

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

## 5. Claim it

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

## 6. Launch it

```sh
cd <repository>
claude --bg --add-dir ~/workspaces/github/botropolis-city -w item-NNN -n "item NNN" "<the kickoff prompt>"
```

Keep `--add-dir` before the other flags: it takes a list of directories, so placed last it swallows the prompt as one more, and the session starts at an empty prompt with nothing to do.

- `-w item-NNN` makes the worktree `<repository>/.claude/worktrees/item-NNN` on the branch `worktree-item-NNN`, from `main`.
- `-n "item NNN"` is the name the claim records; `claude agents`, the city and the status line all show it.
- `--add-dir` gives the session the roadmap, the roadmap skills and, for a vision item, `vision/`.
- The session runs in Aria's default permission mode; nothing here changes it.

It prints `backgrounded · <id> · item NNN`.
Report the id and `claude attach <id>`, and that this session now manages it: its questions arrive here as messages, to answer with `roadmap-manage`.
If it refuses to start, release the claim (below) and report what it said.

## 7. The kickoff prompt

Fill in the braces and send the rest as written: every worker starts cold, so this is the whole hand-off.
Leave out the two lines marked *vision* for a normal item.

`{manager}` is this session's own name, because the session that launches an item manages it (`roadmap-manage`):

```sh
claude agents --json | jq -r --arg s "$CLAUDE_CODE_SESSION_ID" '.[] | select(.sessionId == $s) | .name'
```

If that prints nothing, or a name another live session shares, ask Aria to give this session a name with `/rename` before launching.

```text
Work roadmap item {N}, "{title or public name}". This worktree is yours alone: other agents work in their own, beside you, and everyone lands on main.

The roadmap and its skills are in {meta root}, which this session can read and write; the code is this worktree of {repository}.

1. Read the item, {meta root}/roadmap/{file}, and everything it links to.
   (vision) Its details are private: read {meta root}/vision/items/{file}, and the vision documents it links to.
2. Start from the latest main: git fetch github && git rebase github/main.
3. Work the way the CLAUDE.md files say: test first, red then green.
   Your manager is the session named "{manager}". It speaks for Aria on everything the roadmap and the vision already decide, and asks Aria the rest, so treat its answers as hers. Send it your questions and your test tree with SendMessage, and wait for its reply, instead of asking Aria in this window; before writing a test file, send it the tree, unless the item records a tree Aria agreed. It cannot approve a permission prompt for you: those still come up here for Aria.
   When you render a frame for Aria to judge, send the manager its path and carry on with the next slice.
4. Land each slice as soon as its tests pass: git fetch github && git rebase github/main, run make lint and the tests again, then git push github HEAD:main. Every commit cites "item {N}" and is signed; check with git verify-commit HEAD. Run make publishable before any push that adds an image.
5. When a slice lands, add "Landed: slice K (`<sha>`, r<N>)." under the item's Depends on line in {meta root}, then commit and push it there, and tell the manager in one line. Items waiting on that slice read that line.
   (vision) This is a vision item: never quote its details, the vision documents or the reasoning behind them in anything public — commits, code comments, docs, frames, the changelog. Say what the code does and cite the item number; the details stay private after it ships.
6. When everything the item asks for has landed, close it with the roadmap-close skill, from {meta root}. If you stop before that, release it with the Release steps in the roadmap-start skill, so it is not left claimed.
```

## Release

When a session stops before its item is done, or Aria takes an item back:

1. Make sure every slice that landed has its `Landed:` line.
2. Rewrite line 3 back to `**Open. Filed …**`, dropping the claim and nothing else.
3. `make docs-check`, commit `Release item NNN: <title or public name>`, then pull with rebase and push.
4. `claude stop <id>` if the session is still running; its conversation is kept, and `claude respawn <id>` brings it back.

## Tidy

Once an item is closed or released and its session has stopped, `claude rm <id>` takes the session off the list and removes its worktree and branch; the transcript stays, and `claude --resume` still finds it.
It refuses while the worktree holds uncommitted changes or unpushed commits, and names them: land or release those first, and never pass the flags its refusal offers to discard them.
If it says the worktree is locked by a session that has exited, `git -C <repository> worktree unlock .claude/worktrees/item-NNN` and run it again.
Left alone, Claude Code's sweep removes the worktree anyway once it holds nothing unpushed and is older than `cleanupPeriodDays`.

## Report

The item, the session's id and name, where its worktree is, and how to attach.
If it could not start, say which check stopped it and what would clear it.
