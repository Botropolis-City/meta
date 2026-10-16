---
name: roadmap-add
description: >-
  File new work on the botropolis roadmap as numbered items. Use when asked to
  add something to the roadmap, file a bug or request, or record a defect or
  ask for later. Researches the item against the code first, checks it is not
  already filed, writes roadmap/NNN-*.md with its status line, lists it in
  ROADMAP.md's open table, runs make docs-check, and commits to main.
---

# Add a roadmap item

CLAUDE.md's "Where writing goes" is the contract; this fills it in.
Run it from the meta repository's root, `~/workspaces/github/botropolis-city`: the roadmap lives there, and the app is the `botropolis/` child.
An item is one numbered file in `roadmap/`; `ROADMAP.md` is an index and only gets one row per item.

## 1. Check it is not already there

Search before numbering, because a duplicate is worse than a late item:

```sh
grep -rliE '<two or three distinctive words>' roadmap/ ROADMAP.md vision/items/ 2>/dev/null
```

Read anything that matches.
If an existing item covers it and is **Open**, add to that item instead of filing a new one.
If it covers it and is **Done** or **Fixed** and the problem is back, file a new item that cites the old one by number: numbers are never reused, and a closed item's record is not reopened.

## 2. Research it

An item has to let the next session start without re-deriving anything.
Find the mechanism in the code — the file, the function, the line that gates it — and say what the fix would touch, including the tests that pin the current behaviour and the comments it would make wrong.
Cite evidence a reader can reproduce: a frame in `botropolis/docs/screenshots/`, a shot in `botropolis/dist/demo/` with pixel coordinates, a command and its output.
This repository is public: do not add an image without looking at it and adding it to `tools/reviewed-images.txt`, which `make docs-check` enforces; citing a reproducible shot is usually enough.
If the request rests on a belief that turns out to be wrong, say so in the item and in the reply, with what is actually true.

## 3. Number it

```sh
git fetch -q github && git status -sb | head -1     # pull first if main is behind
git ls-files roadmap/ | grep -oE '^roadmap/[0-9]{3}' | sort -u | tail -1
```

The next number is one past the highest tracked, zero-padded to three.
The revision the item cites is the app's, not this repository's: `$(git -C botropolis rev-list --count HEAD)`, written `r<N>`.
Revisions have counted botropolis's commits since the beginning, and the roadmap moving here at r410 did not change that.

## 4. Write it

`roadmap/NNN-<kebab-case-of-the-title>.md`, with the title on line 1, a blank line 2, and the status on line 3. `make docs-check` reads line 3 and nothing else:

```markdown
# 80. <Title as a statement of the problem or the want>

**Open. Filed YYYY-MM-DD (rN), <where it came from>. <Whose call — "Nobody's call — a defect" or "Aria's call — <what she decides>">.**

<Body.>
```

- When Aria asked for it, say so on the status line and quote her words in the body.
- If it cannot start until another item, or one slice of one, has landed, say so on line 5, after a blank line 4: `Depends on: 82 (slice 1), 85`. Plain numbers, never links. Leave the line out when it depends on nothing; `make docs-check` holds the open table's *depends on* column to it.
- Newline after every sentence, as the repo's markdown convention requires.
- Say whose call it is honestly. "Nobody's" means the fix is known and only needs doing.

### A vision item

An item whose details must stay private — anything from the vision interview, an idea that has not shipped — is a **vision item**.
It takes the next number in the same series and is written as two files.

First the details, in the private vision repository, committed and pushed there before anything public, saved under **exactly the stub's filename**:

```markdown
# 85. <the real title>

<Everything an agent needs to build it: what to build, the slices, the tests, links into the vision documents.>
```

saved as `vision/items/NNN-<area>-part-<k>.md`.
The stub's `Details:` line is public, so the details file has no name of its own: a descriptive filename would say what the item is.
Then the public stub, `roadmap/NNN-<area>-part-<k>.md`:

```markdown
# 85. <Area>, part <k>

**Open. Filed YYYY-MM-DD (rN), a vision item: its details are private. <Whose call>.**

Depends on: <item numbers, or nothing>

Details: `vision/items/NNN-<area>-part-<k>.md`, in the private vision repository.
```

- The public name is an area and a part number — *City look, part 1* — never the idea, and the filename follows it.
- The stub says nothing else: no description, no reasoning, no quote. Its whose-call clause is generic too — "Nobody's call" or "Aria's call", never what Aria would decide.
- `make docs-check` enforces the shape whether or not vision is checked out: a title of the form `# N. <Area>, part <k>`, only status, `Depends on:` (always, `nothing` included), `Landed:` and `Details:` lines, and a details path that is the stub's own filename. With vision checked out, it also pairs every stub with its details file, both ways.
- Without vision checked out, a vision item cannot be filed; say so and stop.

## 5. Index it

Add one row to the `## Open` table in `ROADMAP.md`, above the `phase 20 item 3` row:

```markdown
| [80](roadmap/080-the-slug.md) | <what it wants, one line> | <numbers it waits on, or —> | <whose call> |
```

- **Depends on** names other items as plain numbers, never links: `make docs-check` reads any link to an item in `ROADMAP.md` as listing it open, so a linked dependency would stop the item it names from closing.
- For a vision item, *what it wants* is "a vision item; details private", and nothing more.

If it waits on Aria, add a bullet under `## Waiting on Aria` naming the decision.
Detail stays in the item; the row is one line.

## 6. Check, commit, push

```sh
make docs-check          # must report the new count, none missing, open table matches
git add ROADMAP.md roadmap/NNN-*.md
git commit -- ROADMAP.md roadmap/NNN-*.md   # "File item NNN: <title>", with the why in the body (not for a vision item: below)
git pull --rebase github main && git push github main
```

**A vision item's public commit says nothing private.**
Its subject is `File item NNN: <public name>` and its body is one line, `A vision item; its details are private.` — no why, no description, no quote.
The why goes in the vision repository's commit, which is private.
A pushed commit in a public repository cannot be taken back, so this is the step to get right.

For a vision item, commit and push the details in `vision/` first, so the public stub never points at something that exists nowhere.
The roadmap session may commit at the same time; rebase rather than merge, and re-run `make docs-check` if the rebase touched `ROADMAP.md`.
Work is trunk-based: commit to `main`, no branch or PR.

## Report

Say what was filed, by number, and what the research changed: an existing item it extends, a premise that was wrong, a decision it needs from Aria.
