# Roles

The long-running sessions that keep Botropolis-City moving, and how to start each one.
A role is an agent file in `.claude/agents/`, so the same instructions and skills load on any machine, for anyone, on any Claude plan.
Start one from this root with its make target, which names the session so other sessions can reach it with `SendMessage`.

| role | session name | skills | owns |
| --- | --- | --- | --- |
| `roadmap-manager` | roadmap manager | `roadmap-status`, `roadmap-add`, `roadmap-start`, `roadmap-manage`, `roadmap-attach`, `roadmap-close` | `ROADMAP.md`, `roadmap/`, starting items and answering their sessions, relaying to Aria |
| `design-agent` | design agent | `planning-board` | the interview about what Botropolis becomes, in the private `vision/`, and the items it files |
| `performance-manager` | performance manager | `perf-analysis` | `performance/`: the budgets, the method and the reports; running botropolis's `make test-performance` before each release |
| `auditor` | auditor | `roadmap-status`, `roadmap-add` | fresh-eyes audits of the whole city, filed as items |

```sh
make roadmap-manager           # or design-agent, performance-manager, auditor
make roadmap-manager REMOTE=1  # also reachable from claude.ai/code and the Claude app
```

`REMOTE=1` adds Remote Control, which needs a claude.ai subscription login rather than an API key.

```sh
make roadmap-manager RESUME=1     # resume the newest "roadmap manager" session instead of starting fresh
make roadmap-manager RESUME=<id>  # resume that session
```

`RESUME=1` resumes the role's newest session, found by `tools/agent-session`: the newest one started from this root that is still named after the role and received at least one message.
It refuses, and says so, when there is none, rather than starting a fresh session under a flag that asked for the old one.

`make agents` opens a tmux session, `botropolis` (set `AGENTS_TMUX` to change it), with design in window 1, the roadmap manager in 2 and the performance manager in 3, named `benchmark`, all with Remote Control.
Run it again to reattach; it starts nothing new while that session exists.
`make agents RESUME=1` opens the same three windows with each role's newest session resumed, which is how they come back after a reboot or a crash.

## What the roles keep, and where

A role holds nothing a restart would lose.
What it knows lives in files, so a fresh session started from its make target picks up where the last one stopped:

- the roadmap manager reads `ROADMAP.md`, the items, and each item's *Answered while building* notes;
- the design agent reads `vision/`, which only those with access to the private repository have, so without it the role can do nothing useful and says so;
- the performance manager reads `performance/budgets.md`, `performance/method.md` and the reports, which are its baseline;
- the auditor reads the last audit's *where it stopped* notes, first in [item 154](../roadmap/154-a-fresh-eyes-audit-of-the-city.md).

## The rules every agent file keeps

`make docs-check` holds them, and `testing/acceptance/roles_test.py` mutates each one to prove it can fail:

- every role in the table above has `.claude/agents/<role>.md` with that name and a description, and every agent file is in the table;
- no agent file pins a model, so each person's own plan chooses it;
  a person who wants a role on a model of their own sets `MODEL_<role>` in the git-ignored `.env`, with the role's hyphens as underscores, such as `MODEL_roadmap_manager=fable`, and its make target passes it on;
- no agent file uses project memory, which would commit what an agent remembers to this public repository;
- every skill an agent file names exists, in `.claude/skills/` or in `vision/`'s own skills, and one that only `vision/` could hold is reported as unchecked when `vision/` is not here;
- the table is never empty, since every other check passes on nothing.
