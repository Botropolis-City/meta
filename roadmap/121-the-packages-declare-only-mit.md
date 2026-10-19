# 121. The packages declare only MIT, but ship CC0 and OFL work too

**Done 2026-10-18 (`7060a60`, r656). Filed 2026-10-18 (r628), from the art audit Aria asked for. Nobody's call — Aria asked for it.**

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

## Closed

Done 2026-10-18 in `7060a60` (r656), with its changelog entry in `8992c2b`.

- `packaging/nfpm.yaml` declares `license: MIT AND OFL-1.1 AND CC0-1.0`,
  and `packaging/brew/botropolis.rb.in` declares `license all_of: ["MIT", "OFL-1.1", "CC0-1.0"]`.
- `tools/check-packages` checks both fields against a fixed list in the script, not one derived from the tree.
  It refuses a missing field, a dropped licence and an `OR`, which offers a choice rather than declaring all three.
  With built packages in `dist/` it also checks the rpm's License tag and the Arch package's `.PKGINFO`, so a correct field that the packager drops is caught too; the deb has no licence field.
  `--licences` runs only the field check, and `--root` points it at another tree.
- `testing/acceptance/packages_licence_test.go` runs it against the repository, and against copies with each field mutated: each licence dropped, joined with `OR`, and removed.
- An Arch package built with CI's nfpm (v2.43.0) reads `license = MIT AND OFL-1.1 AND CC0-1.0` in its `.PKGINFO`, and `namcap` says nothing about licences.

**The AUR packages, for the next release.**
The item named `botropolis-git`, but the AUR checkout is `~/workspaces/aur/botropolis`, a package built from tagged releases, and that is the one changed (agreed by the manager, 2026-10-18).
Following Aria's ruling (2026-10-18), both PKGBUILDs set `license=('MIT' 'OFL-1.1' 'CC0-1.0')`, with `.SRCINFO` regenerated and `namcap PKGBUILD` clean, and are committed, signed but **not pushed**:
`dacfa33` in `~/workspaces/aur/botropolis` and `1c33154` in `~/workspaces/aur/botropolis-bin`.
`pkgrel` was not bumped, since the release bumps `pkgver` and resets it; they go out with that version bump.
The botropolis-bin commit also updates a comment that said a licence audit looks for `license=MIT`.
