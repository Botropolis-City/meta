---
name: roadmap-attach
description: >-
  Open a tmux window attached to every running roadmap item session — the
  background sessions roadmap-start launched, named "item NNN". Use when asked
  to attach to, watch, open or show the running item sessions or agents.
---

# Attach to the running items

Run it from the meta repository's root, `~/workspaces/github/botropolis-city`:

```sh
tools/attach-items
```

It gives each live `item NNN` session a window named `item-NNN` running `claude attach <id>`, in item order; leaves a window that already exists alone, so running it again picks up items started since; and closes a window whose session has gone.
`--dry-run` says what it would do.

A session cannot open a terminal on Aria's screen, so the windows go into a detached tmux session named `items` unless this is already running inside tmux, where they join the current tmux session.
Tell Aria the one command to see them, in a terminal of her own: `tmux attach -t items`.
Inside each window, `←` goes to agent view and `Ctrl+Z` drops to the shell; the item session keeps running either way.

Report which windows were opened, which were already open, and which were closed.
