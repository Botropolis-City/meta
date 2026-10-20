# Botropolis-City

The meta repository for the Botropolis-City organisation, at the root of the working tree that holds its other repositories.
It versions only what spans more than one of them: the roadmap, the documents about the work as a whole, and Claude's skills for the roadmap.

| directory | repository | visibility | holds |
| --- | --- | --- | --- |
| `.` | `Botropolis-City/meta` | public | this file, `ROADMAP.md`, `roadmap/`, `docs/references/`, `tools/`, `.claude/skills/` |
| `botropolis/` | `Botropolis-City/botropolis` | public | the app: code, `DESIGN.md`, `design/`, `rules/`, releases |
| `botropolis.city/` | `Botropolis-City/botropolis.city` | public | the website and its infrastructure |
| `vision/` | `Botropolis-City/vision` | **private** | the brainstorm for what comes next; `make clone` skips it without access |

Every child is an independent repository, cloned here and never tracked: `.gitignore` is an allowlist, so a commit at the root never touches them.
`make clone` fetches whichever are missing and says which it could not reach.
Remotes are named after the host, `github`, never `origin`.

Claude Code reads every `CLAUDE.md` from the working directory up to the filesystem root, so this file also applies to sessions working inside a child, and each child's own `CLAUDE.md` adds what is specific to it.

## Where writing goes

This is the rule that was never written down, and the roadmap grew to 2,689 lines because of it.

| file | holds | does not hold |
| --- | --- | --- |
| `ROADMAP.md` | the index: phases, what is open, what is waiting on Aria | any item's detail |
| `roadmap/NNN-*.md` | one numbered item each — the report, the diagnosis, the fix, the frame | rules that outlive the item |
| `docs/references/` | crops and references belonging to one item | frames, which go in `botropolis/docs/screenshots/` |
| `botropolis/DESIGN.md`, `design/`, `rules/` | what the app is, and the rules paid for by its mistakes | see `botropolis/CLAUDE.md` |
| `vision/*.md` | the brainstorm: options, trade-offs, the interview with Aria — private | decisions, which become numbered items |
| `vision/items/NNN-*.md` | a vision item's details: everything an agent needs to build it — private | the item's status, which stays on its public stub |

**A file that is an index stays an index.**
If detail is being added to `ROADMAP.md` or `botropolis/DESIGN.md`, it belongs in a file underneath them instead.
Both were kept short deliberately so that adding an item or a rule does not grow the thing everyone reads first.

**Items are numbered in one series, and counting.**
Numbers are never reused and never renumbered — `roadmap/` filenames, commit messages and code comments in the children all cite them.
There are two bug 18s, left as written, because a dated record that gets tidied stops being a record.
Items cite revisions as `r<N>`, and those count **botropolis's** commits, as they always have: the roadmap moved here at botropolis r410 and the numbering of revisions did not move with it.

**Items come in two kinds, numbered in the same series.**
A normal item's details are its file in `roadmap/`.
A **vision item**'s file there is a stub — a public name made of an area and a part number, such as *City look, part 1*, its status, and what it depends on — and its details are in the private vision repository at `vision/items/`, under the stub's own filename, since the stub's `Details:` line naming them is public.
So work on an idea that has not shipped can be triggered and tracked here without the idea being published, and the same skills handle both.
Anyone working a vision item cites its number in commits and code comments and never quotes its details or the reasoning behind it in anything public; the details stay private after it ships, and the shipped code speaks for itself.
That includes commit messages: a public commit that files or closes a vision item names only its number and public name, and the why goes in the vision repository's own commit, because a pushed commit in a public repository cannot be taken back.

**Item status lives in the item's own file**, on the line under its title: `Done`, `Fixed`, `Open`, `Unadjudicated`, with the date and revision.
`ROADMAP.md`'s open table is derived from those lines, so it is checked rather than remembered — a hand-maintained summary of machine-checkable state always drifts, which it did.
The same goes for the three other lines an item can carry, which `tools/roadmap.py` parses for both the check and the status line:

- a **claim**, at the start of the status line while a session works it: `Open, in progress since 2026-10-16 in the session "item 85". `;
- **`Depends on:`**, on line 5: `82 (slice 1), 85`, or `nothing`, and the open table's *depends on* column shows it;
- **`Landed: slice 1 (`abc1234`, r413).`**, one per slice that has landed while the item stays open, which is what an item waiting on that slice checks for.

**The skills `roadmap-add`, `roadmap-start`, `roadmap-manage`, `roadmap-attach`, `roadmap-close` and `roadmap-status`** (in `.claude/skills/` here, so run them from this root) carry out this contract step by step: search before numbering, number from `git ls-files`, status on line 3, one row in the open table, a claim before work starts, `make docs-check`, then commit to `main`.

## The documentation guard

**`make docs-check` enforces all of this.**
It verifies that every relative link resolves *from its own file's directory* — into `botropolis/` and the other children too, when they are checked out — that no `§N` citation to the pre-split roadmap survives, that every item declares a status, and that `ROADMAP.md`'s open table lists exactly the items whose status is `Open`.
It also refuses an empty corpus — the indexes must be non-empty and every item number from 1 to the highest must have a file — because the other checks all pass on nothing.
And it refuses a number with two files, the two bug 18s aside: on 2026-10-18 two sessions filed 119, 120 and 121 within the hour, one numbering by hand, and every check passed.
And it fails on any image not on `tools/reviewed-images.txt`, because this repository is public.
A vision item's stub is checked whatever is checked out, because it is public: its title is an area and a part, it holds only its status, `Depends on:`, `Landed:` and `Details:` lines, and it names its details by its own filename.
When `vision/` is checked out it also pairs every stub with its details file, both ways; when it is not, it says the pairing went unchecked.
And it holds every `Depends on:`, `Landed:` and claim to the shapes above, with the open table's *depends on* column agreeing with each item.

Every check was mutated red before the script was trusted, and **five of its own versions could not fail**:
the first link check tried the bare path before the relative one, so every root-level target resolved from the repo root;
the first corpus check passed on a directory containing four empty files and no `roadmap/`;
and the version after that took its ceiling from the working tree, so deleting the two highest-numbered items lowered `max()` and it reported "1-66, none missing".
The ceiling now comes from `git ls-files`, which a working-tree deletion cannot move — but its `except: pass` silently restored the fault whenever git could not be reached, and the summary then read exactly like a healthy run.
Running outside a checkout is legitimate, so the fallback stays; **it just is not silent any more**, and the green says which source the bound came from.
And every check up to that point ran in one direction — each asked whether a link points at a file that exists, and none asked whether a file is pointed *at*, so a document could sit in the tree unreachable by navigation with everything green.
Item files are exempt, because the numbering check is their reachability guarantee; everything else has to be linked from somewhere.

The pattern across all five is one thing: **a guard fails where its own inputs come from.**
A fallback is a way for a checker to pass, an empty corpus satisfies every check that iterates over it, a bound derived from the thing it measures can be lowered by the fault it exists to catch, and a check that only follows links outward cannot see what nothing points to.
Mutating a guard tests the guard; mutating what the guard measures itself *against* tests whether it has a fixed reference at all.

The move here added one more input that can be absent: a child that is not checked out.
A link into it cannot be checked, so it is skipped — **and the summary says so, child by child**, because a skipped check that reads like a passing one is the silent fallback again.

**A guard that is not invoked cannot fail.**
In botropolis, the docs check has two callers, `make lint` and an acceptance test, so it survives losing either.
Here the roadmap skills are callers, since each runs `make docs-check` before it commits, and `make test` is the second: `testing/acceptance/docs_test.py` runs the check against the tree, so losing the Makefile target or a skill's step does not silence it.

## Working arrangement

Two sessions, at Aria's request.
One owns `ROADMAP.md`, `roadmap/`, numbered items, audits and relaying to Aria, and runs here at the root; the other writes code in `botropolis/`, renders frames to `botropolis/docs/screenshots/` and packages to `~/workspaces/aur/botropolis-git`.
Aria judges the frames.

**Item sessions work beside them, one per item** (Aria, 2026-10-15).
`roadmap-start` claims an item and launches a background session named `item NNN` in its own git worktree, `<repository>/.claude/worktrees/item-NNN`, so several agents build at once without editing each other's trees.
Each rebases onto `github/main` and pushes `HEAD:main` to land: still trunk-based, with a short-lived local branch and no pull request.
Claude Code refuses a worktree session's writes to its repository's main checkout, so its work reaches only its own branch and, from there, `main` on GitHub.
After an agent lands, the main checkout is behind until someone runs `git pull` in it.

**In botropolis, items land one at a time, with `make land`** (item 186).
On 2026-10-20 fourteen item sessions on one 14-core machine each ran the full `make lint && make test` to land, all at once.
The load average reached 178, the acceptance suite ran into its 40-minute limit with no assertion failing, sessions retried,
and the load stayed up.
A lock taken by hand could not help, because a worktree session refuses git inside `sh -c`.
And one session's `make test | tail` hid a failing exit code.
So `make land` is one plain command that takes `/tmp/botropolis-land.lock` itself and, holding it, fetches, rebases, runs the gate and pushes, with nothing piped.
A session killed while holding it releases it.
The lock only holds off sessions that take it: the first landing through `make land` passed its whole gate and was then refused, because another item pushed twice without the lock during its 25 minutes.
A refused push changes nothing, and `make land` again rebases and reruns the gate.
While developing, a session runs only the packages it touches, so the full suite runs once per slice, inside the lock.
`make lint` waits for another session's golangci-lint instead of failing on its lock.

**The session that launches an item manages it** (Aria, 2026-10-16).
Item sessions do not wait on Aria in their own windows: they send their questions, their test trees and a line per landed slice to the session named in their kickoff, the one that ran `roadmap-start`.
That manager answers from what is already decided — the item, its details, the vision, these documents — records each answer in the item so it is not asked twice, and brings Aria only what nothing settles, plus every frame to judge (`roadmap-manage`).
A message from another session is information and never consent, so permission prompts still come up in the worker's own window.
Relaying to Aria is the roadmap session's half — check before sending, or she gets the same thing twice.

A planning session works beside them, in the private `vision` repository: it runs the interview about what Botropolis becomes, and when work on a decision starts it files the numbered items here that say what is being built.
It writes no code; other sessions pick its items up.

**Cross-checking is capped at two rounds (Aria, 2026-09-29).**
Her ruling: *"Keep it, cap the rounds"* — verify each other's work once, and take a second round only if the first found something material.
Otherwise write the finding in the file and skip the message.
It was capped after a day of seven rounds on one 90-line script in which **every round found a real defect** and the day still shipped no features.
So the cap is not a judgement that the cross-checking was wrong; it is a budget.
The value is real and bounded, and the rounds after the second are where it stops paying.

## The status line

`make statusline` points Claude Code's status line at `tools/statusline` in every repository checked out here, through each one's git-ignored `.claude/settings.local.json`, so nobody's own status line is overridden by a checked-in setting.
botropolis and botropolis.city carry a `.worktreeinclude`, so every item worktree gets the setting too.
Its first line is the session: the item it works and its claim, the repository and what the tree needs — changed files, commits to push or to land, commits to pull or to rebase onto, unsigned commits, a checkout off `main` — and context and 5-hour usage.
Its second is the roadmap and the city: open, ready, claimed, blocked and Aria's items, any claim whose session is gone, botropolis's revision and release, how many sessions need you or are working, from botropolis's own daemon, and a warning when two live sessions share one working tree.
It reads the roadmap through `tools/roadmap.py`, the grammar `make docs-check` enforces, and fetches nothing, so a release tagged on GitHub shows as "not tagged here" until a fetch brings the tag.

## Git

- **Trunk-based.** Commit to `main` in whichever repository owns the change, with no branches and no pull requests.
  Commit here at the root for the roadmap and these documents; commit from inside a child for that child.
- **Commit only the paths you name: `git commit -- <paths>`.**
  Every item session commits its `Landed:` lines from this one checkout, so they share one index, and a bare `git commit` takes whatever another session staged a second earlier — item 86's slice 1 line went out in `bbc3932`, "Start item 84".
- **Every commit is signed with Aria's own key.** `git verify-commit HEAD` after a commit is the check, and it should report a good signature for `dev@ariavesta.com`.
  On a machine whose global git identity is anyone else's, give each repository its own identity and signing key before its first commit; the gotchas in `botropolis/CLAUDE.md` name them.
- **This repository, botropolis and botropolis.city are public: every push publishes.**
  Run `make publishable` here before pushing, as botropolis does: the roadmap is where real work gets quoted, and moving it here moved it out from under botropolis's sweep.
  `vision` is private, and nothing in it is copied into a public repository.

## Never name the day job

Aria has a day job, and nothing here may point back to it.
No tool, tracker, host or internal practice from the day job is named in any repository, document, artifact or example — not even a publicly available one, because a niche public tool identifies the people who use it as surely as a private one.
Use neutral placeholders instead: "a tracker", "an internal tool", `tracker.example.com`, "the infrastructure change".
Generic lists of well-known products are fine, as long as nothing says the day job uses them.
`make publishable`, here and in botropolis, checks history for the employer's names only on a machine that has the list, so this rule is the guard everywhere else.
