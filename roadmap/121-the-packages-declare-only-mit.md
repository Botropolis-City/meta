# 121. The packages declare only MIT, but ship CC0 and OFL work too

**Open, in progress since 2026-10-18 in the session "item 121". Filed 2026-10-18 (r628), from the art audit Aria asked for. Nobody's call — Aria asked for it.**

Aria, 2026-10-18: *"Make sure that for anything we pulled from an asset pack we have followed their licensing and attributed and thanked them."*

The binaries embed Inter (SIL OFL 1.1) and Kenney's atlases (CC0), and every package already installs those licence texts under `/usr/share/licenses/botropolis/`.
What the packages *declare*, though, is MIT alone:

| package | field |
| --- | --- |
| deb and rpm | `botropolis/packaging/nfpm.yaml:15`, `license: MIT` |
| Homebrew | `botropolis/packaging/brew/botropolis.rb.in:7`, `license "MIT"` |
| AUR `botropolis-git` | `~/workspaces/aur/botropolis/PKGBUILD:11`, `license=('MIT')` |
| AUR `botropolis-bin` | `~/workspaces/aur/botropolis-bin/PKGBUILD:9`, `license=('MIT')` |

The OFL's only hard condition, shipping its text with the font, is met, so this is not a breach.
It is the metadata understating what is inside, which is what a distribution's licence audit reads.
Arch's [PKGBUILD guidelines](https://wiki.archlinux.org/title/PKGBUILD#license) want every licence that applies, in [SPDX](https://spdx.org/licenses/) identifiers.

## The fix

- nfpm: `license: MIT AND OFL-1.1 AND CC0-1.0`.
- Homebrew: `license all_of: ["MIT", "OFL-1.1", "CC0-1.0"]`.
- Both PKGBUILDs: `license=('MIT' 'OFL-1.1' 'CC0-1.0')`, with a `pkgrel` bump so the change is published, and `.SRCINFO` regenerated.

`botropolis/tools/check-packages` does not read the licence field today, so nothing would catch the field going back to MIT; it is the place to add that check.

## Done when

All four packages declare all three licences, `namcap` is clean on the built Arch packages, and `tools/check-packages` fails if the nfpm or Homebrew field drops one.

## Answered while building

- **The AUR packages wait for the release** (Aria, 2026-10-18): the licence change to `botropolis` and `botropolis-bin` is committed locally in their AUR checkouts now, without a `pkgrel` bump, and pushed only with the next version, so nobody rebuilds an unchanged version for its metadata.
