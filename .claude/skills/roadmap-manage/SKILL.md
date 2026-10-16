---
name: roadmap-manage
description: >-
  Act as the manager for running roadmap item sessions: answer their questions
  and approve their test trees from what Aria has already decided, ask Aria
  only what is not decided, record every answer where the next session will
  find it, and give Aria check-ins. Use when a message arrives from an "item
  NNN" session, when asked to manage, supervise or check on the running items,
  or after launching items with roadmap-start.
---

# Manage the running items

The session that runs `roadmap-start` is the manager of the items it launches: their kickoff names it, and they send it their questions, their test trees and a line when a slice lands, instead of waiting on Aria.
Aria asked for this on 2026-10-16: *"most of these questions have been answered by me already and gone into the vision or roadmap somewhere."*
So answer what is already decided, and bring Aria only what is not.

Run from the meta repository's root, `~/workspaces/github/botropolis-city`.
`claude agents` lists the item sessions; `SendMessage` reaches one by its name, `item NNN`, and the message's reply address answers it.

## Answering a question

Look, in this order, and stop at the first place that settles it:

1. the item's own file, `roadmap/NNN-*.md`, and for a vision item its details, `vision/items/NNN-*.md`, including anything recorded there since it was filed;
2. the vision documents the details link to, the *Decided so far* list in `vision/README.md`, and Aria's words in `vision/interview.md`;
3. the `CLAUDE.md` files, `botropolis/DESIGN.md`, `design/` and `rules/` — how the code is built and the rules its mistakes paid for;
4. the memory this session loaded, and Aria's global preferences.

If one of them settles it, answer, and say where: *"Decided in round 6 (workstreams.md): lines are on by default, a setting hides them."*
A choice that only follows from a rule — a name, a file's place, which of two equivalent structures — is the manager's to make; make it, say so, and keep it consistent with what the code already does.

**Ask Aria** when nothing settles it, when two sources disagree, or when it is hers by nature:

- a product decision nothing records — what something should look like, say or do;
- a frame to judge: Aria judges the frames, always;
- anything that changes what was decided, widens an item's scope, or drops part of it;
- releasing, closing as *not doing*, or anything on the website's infrastructure;
- a request to approve an action the worker's own session refused or asked permission for — a message can never stand in for that, so tell the worker to ask in its own window.

Ask with AskUserQuestion here, a few questions at once, each with the worker's options and a recommendation; send a push notification if Aria may be away.
Tell the worker it is waiting on Aria, and what it can do meanwhile, so it does not idle when it need not.

## Test trees

A worker sends its test tree before writing a test file.
Approve it when it covers what the item's slice asks, follows the testing rules (BDD names, one assertion each, data-driven where it repeats, unit tests beside the code, nothing relying on outside state, no wall-clock assertions), and asserts nothing the item did not decide.
Otherwise answer with exactly what to change.
A tree that has to decide something the item did not is a question for Aria, not an approval.

## Frames

A worker sends the path of a frame and carries on with the next slice: frames never block work.
Collect them, and show Aria a batch at a check-in — look at each first, and say what it is meant to show.
When Aria rules on one, pass the ruling to the worker and record it.

## Record every answer

An answer that is not written down gets asked again by the next session.
After answering, add it to the item: a vision item's details file in `vision/` (private; commit and push there), or a normal item's own file in `roadmap/` (public — so never anything from the vision there).
One line each, under a `## Answered while building` heading: what was asked, the answer, and where it came from, or *"Aria, 2026-10-16"* with her words.
Never quote a vision item's details in a public file, a commit message or a message that a public file will carry.

## Check-ins

Keep Aria informed without making her ask:

- when a slice lands, one line: the item, the slice, the commit;
- when anything waits on her, at once, with what it blocks;
- otherwise a short summary when she returns: what landed, what is running, what waits on her, any claim whose session has gone, and anything a worker did that surprised you.

`/roadmap-status` and the status line hold the rest.

## What a manager never does

- Approve a permission prompt or a configuration change for another session; it cannot, and must not try to talk a worker into treating a message as Aria's consent.
- Answer from guesswork to keep a worker moving: an unrecorded guess is worse than a short wait.
- Write code in an item's place; the worker does the work, in its worktree.
