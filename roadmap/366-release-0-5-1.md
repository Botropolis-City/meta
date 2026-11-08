# 366. Release 0.5.1

**Open, in progress since 2026-11-07 in the session "item 366". Filed 2026-11-07 (r1333) at Aria's request. Nobody's call — Aria named it and what it holds.**

Depends on: 364, 365, 367, 368

Aria, 2026-11-07, asked whether the fixes for moving sessions between groups ship as 0.5.1: *"Cut 0.5.1 when both land"*.

## What it holds

- [Item 364](364-moving-a-session-into-a-team-s-group-is-dropped.md): moving a session into a team's group, or starting one from it, puts it there, and no two groups share an id.
- [Item 365](365-a-hand-move-into-a-group-does-not-take-in-the-0-5-0-film.md): a group edit made from the map (a move, a rename, taking a session out) takes effect at once, not only after later activity in `~/.claude`. The notice says "moved" only once the move has taken.
- [Item 367](367-while-you-were-away-lists-a-session-once-per-time-it-needed-you.md): "While you were away" lists each session once, with how many times it needed you, added by Aria the same day.
- [Item 368](368-teststoredheftspass-races-under-race.md): the data race in `pkg/state`'s stored hefts, added by Aria the same day: *"Let's fix that race as part of 0.5.1 as well"*.
- Everything else on `main` when the candidate is cut, item 361's glossary among it.

## What it runs

As 0.5.0's did ([item 354](354-release-0-5-0.md)): the tag rests on the automated checks, and the performance gate runs on the `performance` profile, recording the machine's power state (item 358). Then the re-film, the release, the AUR on Aria's standing approval, and the site's media, whose upload needs Aria's 1Password.
The re-film includes item 362's scenarios. Its move-in and convoy shots, dropped from the 0.5.0 film because moves didn't take, come back from this release's build, and item 360 puts them on the site.
0.5.0's soak has not run yet, so it runs once on this release instead.

## Answered while building

- **Do it all** (Aria, 2026-11-07, *"Do it all."*): the release runs to the end on the automated checks, and the roadmap manager pushes the AUR.
  The soak then runs once, on this machine, overnight, on the released build (`make perf-soak`), and its record goes here.
  The site's import of the 0.5.1 film follows. Its upload needs Aria's 1Password, so it waits for her if she is away.
- **Ship on the Intel runner's red** (Aria, 2026-11-07, *"Ship; fix 355 right after"*). CI on `a9bfaad7` failed twice on `macos-26-intel`, both times only in `tools/land-queue`'s slow-waiter test ([item 355](355-the-landing-queue-s-slow-waiter-test-times-out-on-macos-intel.md)). That tests a development tool that ships in no package. Everything else was green: the other macOS runner, lint and every package.
  Item 355 starts right after the tag.
- **The film's moves may still not take** (item 366's session, 2026-11-07). A city run with `--headless`, `--record` or `--script` works in a private copy of the state directory (item 114), so its moves reach no daemon.
  If `groups-moves.yaml`'s shots show no move, they are left out again, the release goes on, and the film tooling becomes a new item. Item 365's fix itself passed L1–L2's move checks, in 83 ms on a quiet home.

## Released

- **Released** (2026-11-07): run 42440854994 tagged `v0.5.1` at `a9bfaad7` (r1343) and published 18 assets at 03:33 UTC on 2026-11-08, with the package repositories and the Homebrew tap, both macOS runners included, green.
  The dry run, 42438627729, was green at the same commit.
  The candidate is one commit: VERSION and the [0.5.1] section, which gathers everything under [Unreleased].
  It landed through `make land` with S1–S10 in its gate.
  Its CI, 42434517185, was red twice on `macos-26-intel`, only in `tools/land-queue`'s slow-waiter test (items 355 and 357). Aria ruled to ship and fix 355 right after.
  A third attempt of that job passed, since the release workflow takes only a green CI run, and the packages released are the first attempt's.
  The amd64 and arm64 packages matched `SHA256SUMS`, and their binaries report 0.5.1.
- **The performance gate**: every check green, with `settle` quiet at once, on platform profile `performance`, governor `powersave`, EPP `balance_performance`, turbo on and RAPL long- and short-term at 57 W, the same before and after (item 358).
  The rescan at 2,000 sessions took 11.9 ms median against 16 (11.2–12.7). The fitted 600-district frame took 14.8 ms against 16, zoomed 5.9 and panned 5.8 against 10.
  The 2,400-session city settled at 441 MiB under 512, and the daemon at 2,000 sessions at 55 MiB under 64.
  Skipped by design: `TestCalibrateCoreRate` and `TestLightCycleOnARealGPU`.
- **L1–L2, side by side**, as 0.5.0's: the candidate's daemon, from CI's tarball, ran on its own socket, config copy and state, cache and runtime directories, reading the real `~/.claude`. No sudo was used, and Aria's daemon was left alone.
  L1 passes: 416 sessions, 59 jobs and 10 records, matched by id in one pass.
  Two background sessions that the CLI called working against its own idle record, each ending on a Stop hook, show needs-you: the CLI disagreeing with itself, as ruled at 0.3.0.
  One that armed its own wakeup shows waiting, and seven jobs with no transcript are not shown, by design.
  L2 passes: a stopped throwaway session left `claude agents --all` and the daemon 2 s after `botropolis rm`, and stayed off across a restart of the side daemon.
- **The move check** (item 365): a move made with the candidate's city into a group took 83 ms from the write to the daemon's snapshot on a quiet staged home, where nothing had been written for a minute before.
  On the side daemon over the real home it took 147 ms, and it survived a restart.
  The city ran on a private virtual display, and Aria's own groups were untouched.
- **The re-film**: `make demo-media` at `a9bfaad7` filmed 67 shots in 107 files.
  Its move-in and convoy shots still show no move: a scripted city keeps its state in a private copy, so the shot's daemon never sees the move. That is the film tooling, not the fix, and it is filed as [item 371](371-the-demo-film-cannot-show-a-move-taking.md).
  Both shots are left out of the film handed to item 360: 103 entries, kept outside the worktree, with a contact sheet of its 66 stills beside it.
- **The AUR** (2026-11-07): `botropolis` `29d79b8..daa5423` and `botropolis-bin` `fbd0e03..ab8a3e3`, both 0.5.1-1, their sources checked against the release, pushed by the roadmap manager on Aria's standing approval.
- **The site**: [item 360](360-the-website-still-describes-the-city-of-0-3-0.md) imported the film. Its upload waits for Aria's 1Password.

Deviations, all ruled by Aria: A1–A7 were waived; the tag rests on the automated checks alone; L1 and L2 ran against a candidate daemon beside hers; and the release shipped over the macOS Intel slow-waiter test, with item 355 to be fixed right after.
The soak runs once, on the released build, and its record goes here. A first start ran about a minute and was stopped before it measured anything, so that item 369 could land first.
