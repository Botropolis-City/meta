# 349. Release 0.4.1

**Done 2026-11-07 (`f70cb32d`, r1277). Filed 2026-11-06 (r1260) at Aria's request. Nobody's call — Aria named the version and what it holds.**

Depends on: 343, 344, 345, 346, 347

Aria, 2026-11-06, to the roadmap manager, on the six items she filed from dogfooding 0.4.0 on her laptop: *"let's do them as new versions"*,
and, offered 0.4.1 for the five fixes with 0.4.2 for item 348 after its frame rounds, she chose one version: *"One version, 0.4.1"*.

## What it holds

Items 343, 344, 345, 346 and 347, filed 2026-11-05 from her own sessions: the fixes she can have before her workday.
Fixes make a 0.x.Y under the pre-1.0 rule, so 0.4.1.
Everything else on `main` when its candidate is cut ships with it.

**Split from the rest on 2026-11-06.**
This item first held items 340 and 348 too, then also the controls redesign, items 350 to 353 (Aria, through the design agent: *"I'd like this all to land in the next release whether it's 0.4.1 or 0.5.0."*).
Told that item 348's frame rounds and the controls chain put one release of all of it at a weekend's distance while the five fixes could land by morning, Aria chose: *"Do the split, but let's not soak until after 0.5.0"*.
So 348, 350 to 353 and 340 are [item 354, Release 0.5.0](354-release-0-5-0.md), and this one ships first.

## What it runs

[RELEASING.md](../botropolis/RELEASING.md) as 0.4.0 did (item 338), **with the soak waived** (Aria, 2026-11-06): one candidate, a landing freeze from it to the tag, the re-film, S1–S10, L1–L2, A1–A7, the dry run, the release, the AUR packages and the site.
The soak runs once, after 0.5.0, and covers both; item 354 carries it.
Manual checks stand across a re-cut; automated ones re-run.

The performance gate's rescan check (`TestARescanAtTwoThousandSessions`, item 340) was red at 0.4.0 and Aria shipped on it (*"Ship; soak now"*, 2026-11-03); nothing in this release touches the rescan, so it ships the same way and item 340 lands in 0.5.0.
If anything else in the gate is red, that is new and stops the release.

## Answered before it ran

Aria, 2026-11-06, before going to bed, to the roadmap manager:

- **A1–A7 are waived as well as the soak**: *"Waive A1–A7 too, tag overnight"*.
  The release tags and publishes on the automated checks alone; anything that needs 1Password on her screen — the AUR pushes, the site's media — waits for her in the morning.
- **The landing freeze is lifted for 0.5.0 work** (*"Lift it for 0.5.0 work"*): items 348, 350 and 352 land on main after the candidate is cut, the tag still targets the candidate commit, and a re-cut, if one is needed, is made from that commit rather than from main.
- **The rescan check ships red** (*"Ship, 340 in 0.5.0"*), as 0.4.0 did; anything else red in the performance gate stops the release.
- **L1 and L2 run against a candidate daemon beside hers** (roadmap manager, 2026-11-06, asked by the release session): installing the package needs `sudo` on Aria's screen, and her live daemon serves the city and the working sessions overnight, so it is neither replaced nor restarted.
  The candidate's `botropolisd` from the CI tarball runs as a second daemon with its own socket, config copy and state directory, reading `~/.claude`, and L2's restart is a restart of that daemon; if its state cannot be kept apart from hers with certainty, they run against her installed 0.4.0 daemon as partial checks, the full ones listed for her morning, and that does not block the tag.
- **The candidate's performance gate is red on a new check** (release session, 2026-11-06): `c7beff07` meets every budget but two — the rescan, which ships red by Aria's ruling, and `TestACityOfSixHundredDistrictsFrames` fitted, at 24.9 ms of CPU a frame against 16 and 127.9 M instructions a tick, which 0.4.0 met.
  The release stops on it: the test is rerun at the candidate and at v0.4.0 on a quiet machine, comparing instructions a tick, and if it is real, the commit that costs it is fixed on main and the candidate re-cut as `c7beff07` plus that fix alone.
  So the 0.5.0 work lands only after 0.4.1 is tagged, though the freeze was lifted for it.
- **It is the machine, not the code** (release session, 2026-11-06): the fitted 600-district frame does 127.9 M instructions a tick at the candidate and 127.8 M at v0.4.0, and v0.4.0 fails the same check on this machine tonight (21.9 ms against 16); the candidate's settled rerun took 18.4 ms.
  Zoomed and panned cost 1.3% more instructions at the candidate and pass at both.
  The release waits for Aria's ruling, since hers was that anything red besides the rescan stops it; a changelog commit moving item 352's slice 1 line into [0.4.1], whose code is in the candidate, is ready and unpushed.

## The checks

- **The performance gate** (release session, 2026-11-06): `make test-performance` at `c7beff07`; everything met but `TestARescanAtTwoThousandSessions` (red as ruled, item 340) and the fitted 600-district frame in `TestACityOfSixHundredDistrictsFrames`, 24.9 ms of CPU against 16, then 18.4 ms on a settled rerun.
  v0.4.0's own build, run back to back, fails it too, at 21.9 ms: 127.8 M instructions a tick there against 127.9 M at the candidate, so the work is unchanged and the machine is slower per instruction than on 2026-11-03.
  It stops the release under Aria's rule; hers to rule in the morning.
- **Step 2** (release session): the packages from CI 42238116877, amd64 and arm64, with `SHA256SUMS` verified and the binaries reporting 0.4.1; S1–S10 pass in the candidate's `make land` gate; dry run 42247222190 green at `c7beff07`.
- **L1–L2, side by side** (2026-11-06, the manager's ruling, so that no sudo was used and her daemon was left alone): the candidate's `botropolisd` from the CI tarball ran as a second daemon on its own socket, config copy and `XDG_STATE_HOME`, `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, reading the real `~/.claude`, with the candidate's CLI pointed at it.
  L1 passes: 393 sessions, 57 jobs, 10 live records, every live one agreeing (busy→working, a handed-back turn→needs-you, one blocked→waiting as at 0.4.0, an unprompted session→empty); the 7 jobs not shown have no transcript, by design.
  L2 passes: a stopped throwaway session in the scratch folder left `claude agents --all` and the daemon by the first check after `botropolis rm`, and stayed off across a restart of the side daemon.
  Its transcript remains, as designed, so her own 0.4.0 daemon may show it resting in *valley*.
- **No shipping into a red check** (Aria, 2026-11-06, in the morning): *"The machine is quiet. I don't want things to go down hill, so re-run or investigate or whatever we need"*.
  The fitted 600-district check is rerun on the quiet machine at the candidate and at v0.4.0; if the candidate passes, it ships; if it stays red, the machine or the code is investigated before it does.
- **The re-film passes** (Aria, 2026-11-06, on a contact sheet of its 52 stills at `f70cb32d`): *"Pass, publish with 0.4.1"*; 51 shots, 80 files, imported into the site with the release.
- **CI at `f70cb32d`** went green on its second attempt (run 42265186145): the first failed only on the Intel macOS runner, in item 355's land-queue test and in `pkg/daemon`'s `TestRequestRescan`, seen failing there for the first time; dry run 42269229104 green.

## Released

- **Released** (2026-11-06): run 42273170661 tagged `v0.4.1` at `f70cb32d` (r1277) and published 18 assets at 19:12 UTC, with the package repositories and the Homebrew tap (both macOS runners) green.
  The re-cut from `c7beff07` to `f70cb32d` carries only item 352's slice 1 changelog line, moved into [0.4.1], since that slice's code was in the candidate; its CI, 42265186145, went green on a rerun of the Intel macOS job, and its dry run is 42269229104.
  The 600-district frame passed three alternating pairs at `c7beff07` once the platform profile was performance (13.93 ms median against v0.4.0's 14.10, bar 16); the earlier reds were the balanced profile (item 358).
- **The AUR** (2026-11-07, pushed by the roadmap manager on Aria's approval given to it directly): `botropolis` `298813e..59304e6` and `botropolis-bin` `854412d..5190213`, both 0.4.1-1, sources verified against the release.
- **The site** (2026-11-07): the re-film's media, 52 images and 32 clips, imported (`d819547` in botropolis.city), uploaded by Aria's 1Password approval, and deployed by run 42366793758; botropolis.city shows v0.4.1.

## Closed

0.4.1 shipped items 343 to 347, plus item 352's first slice, which was on main when the candidate was cut.
Deviations, all ruled by Aria: the soak and A1–A7 were waived; L1 and L2 ran against a candidate daemon beside hers rather than an installed package; the rescan check shipped red, as at 0.4.0, and item 340 has since brought it under its bar; the frame check stopped the release until the profile was found, and Aria chose to fix the machine rather than ship into a red.
The soak runs once after 0.5.0, item 354.
