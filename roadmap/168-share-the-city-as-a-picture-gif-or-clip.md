# 168. Share the city as a picture, GIF or clip, in a sharing mode

**Done 2026-10-20 (`5c12f98`, r815). Filed 2026-10-20 (r786) at Aria's request, from item 167's analysis. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`6be1962`, r801).
Landed: slice 2 (`9a85987`, r809).
Landed: slice 3 (`5c12f98`, r815).

Item 167's command-line analysis found that `p` already saves a PNG of the city, and offered a recording key and a "for sharing" mode as options.
Aria, 2026-10-20: *"I like the idea of sharing mode. That allows you to take a png or gif or clip."*

## What it is

A sharing mode in the city: entered by a key (and from the reference), it shows the city as it would be shared — with what identifies the person hidden: session titles, project and district names (a neutral name each, stable for the capture), spend and token figures, prompts and card text — and offers three captures:
- **picture**: a PNG of the window;
- **GIF**: a short loop (a few seconds, sized for a chat or an issue);
- **clip**: an MP4 or WebM of a chosen length.
Each says where it saved, and opens the folder on request. Recording uses the city's own clock, as the demo recorder does (items 113, 117), not screen capture; without an encoder available it says which one is missing rather than failing silently. Leaving the mode restores everything.

Why hide by default: `docs/botropolis.gif` once published a project name, MCP vendor names and a real daily spend from this repository (see `make publishable`); a sharing mode exists so a person cannot do that by accident.

Tests: in sharing mode, no session title, district name, spend or prompt text is drawn (checked against a fixture whose names are unique strings); each capture produces a file of the right type and length; leaving the mode restores the view; a missing encoder is reported. Frames for Aria: the same city normal and in sharing mode, and a GIF.

## Decided while building

- **The shape** (manager, 2026-10-20, approved with the test tree): `shift+s` enters and `esc` or `shift+s` leaves, and the key list's row enters it from the reference; the aliases are *District A*, *Session 3*, *Tower 2*, *Group 1*; usage-limit percentages hide with the spend; captures go to the XDG user dirs (`user-dirs.dirs`), Pictures and Movies on macOS, else home.
- **Aria, 2026-10-20**, on slice 1's frames: the aliases and the map re-fitting to the whole window once the chrome is gone both stand.
- **Shared captures are named `botropolis-share-<stamp>`**, apart from `p`'s screenshots, which hide nothing, so a person can tell which is safe to post; it is also what lets the acceptance test tell sharing's picture from `p`'s.
- **Nothing built from the stand-in names outlives the mode**: the first-run group review, the journal and the statistics prompt wait until sharing ends, and first sightings are neither drawn nor used up while it lasts — otherwise confirming the review after leaving would have saved *Group 1* as a real group's name.
  Item 169 found and fixed a second way in, in its landing: the scene's own rebuilds read the veiled snapshot, so a ledger change or a hide during sharing left the veil on after leaving.

## Closed

`shift+s` shares the city, in release builds as well as dev ones.
Three layers hide what identifies the person, each mutated red before it was trusted:
the **veil** (`pkg/city/veil.go`) copies each snapshot with every identifying word replaced, by a table of every string a snapshot can carry, and `TestVeilAccountsForEveryWord` fails on a string the table does not account for;
**no chrome** — every panel, card, sidebar, footer and figure — is drawn while sharing;
and a **guard** at the only two places text is drawn refuses any name, folder, prompt, spend, token count or percentage that still gets through, and counts it.
`TestSharing` draws a fixture whose every name is a unique string, with the sidebar, a card and the reference open, and expects none of them drawn and the guard to have refused nothing.
The guard's own mutation stayed green until a test checked it is wired to both drawing points; it is now.

`p` saves a PNG, `g` a GIF of 4 s at 15 fps no wider than 720 px (standard library only, a median-cut palette per frame), and `c` a clip of 5, 15, 30 or 60 s (`l`) at 30 fps through ffmpeg.
Recordings run on the city's clock with item 113's lockstep, frames are encoded off the game loop, and the sharing bar is drawn after the capture, so no picture carries it.
The acceptance tests (`testing/acceptance/share_test.go`) take each capture in a headless city: a PNG, a GIF of 60 frames at 720 px, and a 5-second clip that ffprobe reads as 150 H.264 frames.

Frames: `botropolis/docs/screenshots/r798-item-168-workday-normal.png` and `r798-item-168-workday-shared.png` (approved), and `r805-item-168-workday-shared.gif`.

For Aria:
- **The GIF** is the one frame not yet judged: its 720 px width makes labels small, and its length is 4 s.
- **The clip falls back to a WebM**: Fedora's own `ffmpeg-free` has no libx264, so the city picks H.264 in an MP4 where it can, VP9 in a WebM where it cannot, and names both encoders when it has neither.
- **The Arch package does not mention ffmpeg**: nfpm has no optional dependencies for Arch. The deb suggests `ffmpeg`, the rpm `/usr/bin/ffmpeg`, and the Homebrew caveats say `brew install ffmpeg`; the AUR package's `optdepends` would be the place to add it.
- **The guard errs towards blanking**: it matches any word of four letters or more from a session's names, so a landmark label sharing a word with a session title would be left blank while shared.
