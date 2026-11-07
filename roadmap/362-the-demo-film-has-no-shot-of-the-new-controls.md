# 362. The demo film has no shot of the clinic's list, the action menu, the groups board or the keys

**Open. Filed 2026-11-07 (r1331), from item 360's audit of the website. Nobody's call — the shots are what shipped.**

0.5.0's film (`make demo-media`, the scenarios in `botropolis/demo/scenarios/`) has no shot of:

- the clinic's list, opened with `a`;
- the action menu open, from `space` and from right-click, with a column's menu showing;
- City Hall's groups board, opened with `g`;
- every key drawn as a cap while `e` is held.

The website (item 360) needs each one to show its Drive and Groups sections, and ships its text with the stills it has until the next film.

## The fix

Add each as a scenario shot, with a still and, where the move is the point (the menu opening, the board's rename), a clip, and give its caption the changelog's words.
Check them with `make check-demo-corpus` and film them at the next release, as [film at release](354-release-0-5-0.md) does; nothing is re-filmed on its own.
