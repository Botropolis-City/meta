---
name: roadmap-status
description: >-
  Summarise the botropolis roadmap from the item files themselves: what is
  open, whose call each item is, and what is waiting on Aria. Use when asked
  what's on the roadmap, what's open, what to work on next, or what needs
  Aria's decision. Read-only.
---

# Roadmap status

Run it from the meta repository's root, `~/workspaces/github/botropolis-city`.

The item files are the source of truth; `ROADMAP.md`'s open table is derived from them, and `make docs-check` proves the two agree.
Run the check first, so a summary is never built on an index that has drifted:

```sh
make docs-check
```

Then read each open item's status line and title:

```sh
for f in $(git ls-files 'roadmap/[0-9][0-9][0-9]-*.md'); do
  s=$(sed -n 3p "$f")
  case "$s" in "**Open"*) printf '%s\n  %s\n  %s\n' "$f" "$(head -1 "$f")" "$s" ;; esac
done
```

Where each open item stands follows from its file and its row, and `tools/roadmap.py` computes it the same way the status line does: **in progress** when line 3 carries a claim (`Open, in progress since <date> in the session "<name>". `), **Aria's** when the row's *whose call* starts with `Aria`, **parked** when it says `until`, **blocked** when a `Depends on:` entry has not landed (an open item, or an open item without that slice's `Landed:` line), and otherwise **ready**:

```sh
python3 -c 'import sys; sys.path.insert(0, "tools"); import roadmap
items = roadmap.load(); rows = roadmap.open_table(open("ROADMAP.md").read())
for n, it in sorted(items.items()):
    if it.is_open: print(n, roadmap.standing(it, items, rows.get(n)), it.name, sep="\t")'
```

For each claim, check its session is alive (`claude agents`): a claim whose session is gone is stale, and says so in the report.

A file with a `Details:` line is a **vision item**: its stub is public and its details are in `vision/items/`.
When `vision/` is checked out, read the details from there to say what the item is; when it is not, report it by its public name and say its details are private.
Never repeat a vision item's details anywhere public.
Report each item's *depends on* cell from `ROADMAP.md`, so what is ready to start shows apart from what waits on another item.

Report in four groups:
1. **In progress**: each claimed item, its session, since when, and whether the session is alive.
2. **Waiting on Aria**: items whose status names her call, with the decision each needs, in one line.
3. **Ready to do**: "nobody's call" items with nothing left to wait on, with what the fix touches if the item says so; then the **blocked** ones, each with what it waits on.
4. **Parked**: open items filed as curiosities or deferred until something costs.

Note `phase-20-explain-itself.md`'s open sub-item separately; it is not numbered, and the check does not see it.
Do not edit anything. If the check fails, report the failure first; it is the more important finding.
