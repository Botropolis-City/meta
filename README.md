# Botropolis-City

The planning repository for the Botropolis-City projects: the roadmap, and the documents that span more than one repository.

| repository | what it is |
| --- | --- |
| [botropolis](https://github.com/Botropolis-City/botropolis) | the app: every Claude Code session on a machine, drawn as a city |
| [botropolis.city](https://github.com/Botropolis-City/botropolis.city) | the website and its infrastructure |

This repository is the parent directory of the others.
Clone it, then let it fetch the rest:

```
git clone --origin github git@github.com:Botropolis-City/meta.git botropolis-city
cd botropolis-city
make clone
```

Each child is an independent repository and is never tracked here.

## The roadmap

[ROADMAP.md](ROADMAP.md) is the index of what is open and what is waiting on a decision.
Every numbered item has its own file in [`roadmap/`](roadmap/), with its status on the line under its title.
`make docs-check` proves the index and the items agree.

The roadmap lived in the botropolis repository until 2026-10-15, and its history before that is there.
