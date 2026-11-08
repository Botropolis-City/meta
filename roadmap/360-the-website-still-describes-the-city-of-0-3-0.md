# 360. The website still describes the city of 0.3.0

**Open, in progress since 2026-11-07 in the session "item 360". Filed 2026-11-07 (r1331) at Aria's request. Nobody's call — the content is what shipped; Aria judges the frames.**

Landed: slice 1 (`d18f0c4`, r53).
Landed: slice 2 (`93d643a`, r54).
Landed: slice 3 (`a719f04`, r55).
Landed: slice 4 (`48c30df`, r56).
Landed: slice 5 (`cb16dae`, r57).
Landed: slice 6 (`fe3e3ba`, r58).
Landed: slice 7 (`890a067`, r59).

Aria, 2026-11-07, after 0.5.0's media went up: *"So much has changed recently. Let's do a pass of the website and change/update any content that needs to be added as well like the clinic, explanation of groups, etc..."*

## Where it stands

The site's prose was last rewritten for 0.3.0, by item 231 (botropolis.city `157c8b1`, 2026-10-24).
Since then, `make media-import` has refreshed its stills and clips at every release, the last being 0.5.0's (`4b2663f`), and item 267 made its version and news follow the latest release.
Nothing has rewritten what it says.
Between 0.3.1 and 0.5.0, `botropolis/CHANGELOG.md` gained about 80 entries, and the site's components (`botropolis.city/src/components/`: `Hero`, `Glance`, `Views`, `Drive`, `Theater`, `KeysOverlay`, `Install`, `Release`) and `src/data/` never mention groups at all.

What the site does not tell a visitor, from the changelog:

- **The clinic**: the building with the green cross on the plaza, which shows who needs you (0.3.3), and lights its windows at night (0.3.4).
- **Groups**: what a group is and how sessions come to be in one; a group's sessions sitting together as a neighbourhood inside a kerb; the group's line between its districts, and the `group_line_form` setting with its other two forms; the groups board; *move to group*, and dropping a carried building on a group; a teammate following its lead; a group of one; pointing at a grouped session lighting its whole group.
- **The controls**: the action menu with its *Session*, *Project* and *Group* menus, key caps, the list keys shared by every panel, and `/` filtering any list; `shift+n` opening a new session; `d d` to demolish.
- Anything else in `[0.3.1]` to `[0.5.0]` that changes what someone sees or does: the lenses, panels and keys the site already names should be checked against the app as it is now, and the Keys overlay against `config.Bindings`.

## What it wants

A pass over every page and section, checked against `botropolis/CHANGELOG.md` from `[0.3.1]` to `[0.5.0]`, `botropolis/DESIGN.md` and the app itself, which updates what has changed and adds what is missing, groups and the clinic first.
It uses the 0.5.0 re-film's media, which is uploaded and live; a shot the site needs that the film lacks is added to the demo's shot list in botropolis, rather than shot by hand.
The site's words are the changelog's public words: nothing from `vision/`, and nothing about what has not shipped.
Frames of each changed section, at desktop and phone widths, go to Aria through the manager.
It lands in botropolis.city, whose push to `main` deploys, under its own tests (`make test` there).

## Found since

- **The site's `main` is red, and 0.5.0's page has not deployed** (2026-11-07): the media commit `4b2663f` failed `src/data/glance.test.ts`, *"it should sit on an object in the still"*, because three of the Glance hotspots now fall on grass or a plate in 0.5.0's still, not on the object they label.
  0.4.1's page stays live until it is fixed, so this is the first slice: move the hotspots onto what they label in the new still, so the test passes on its own terms, never by loosening it.

## Answered while building

- **The audit and its slices** (roadmap manager, 2026-11-07): approved as proposed. S2 is Glance, with the clinic, City Hall and group hotspots, the full plaza line and the glossary rows. S3 is Drive. S4 is a new Groups section, between Drive and New. S5 is the release block.
  Street stalls stay out, since they are off by default.
- **A hotspot may quote `CHANGELOG.md`** when the app has no wording of its own, as with the kerb: the changelog is public, and the app's own words always win where they exist.
  [Item 361](361-the-station-glossary-entry-outlived-the-stations.md) gives the kerb an entry in the app's glossary, and the site moves to it once it lands.
- **The 0.3.0 block stays as a dated record of 0.3.0**, with "and 0.3.x continues on them" dropped. The site states no measurement newer than one it can cite.
- **Missing shots**: the text ships now with the stills the 0.5.0 film has, and [item 362](362-the-demo-film-has-no-shot-of-the-new-controls.md) adds the clinic's list, the action menu, the groups board and the held `e` to the film for the next release.
- **S2's test tree** (roadmap manager, 2026-11-07): approved. It extends `glance.test.ts`'s loops, adding the clinic, City Hall and group hotspots, a plaza line that names the clinic, glossary rows for the clinic, the kerb and a group's line, and a roads row that names its four vehicles.
  The existing acceptance loops cover the new hotspots' overlap and fit at 360 wide.
- **No City Hall marker yet** (roadmap manager, 2026-11-07): the hall stands only with statistics, which the film lacks, so no still shows it. S2 drops it, the board of groups goes into S4 in words, and the marker comes back once [item 362](362-the-demo-film-has-no-shot-of-the-new-controls.md) films the hall.
- **S3's test tree** (roadmap manager, 2026-11-07): approved. `drive.ts` swaps the old card's chips for the Session, Project and Group menus. A live test checks each menu's labels and keys against `scene.go` and `bindings.go`, and each key line against the changelog. The acceptance spec shows the three menus and no old row of buttons.
- **S4's test tree** (roadmap manager, 2026-11-07): approved. It is a Groups section between Drive and New, with fifteen quoted facts in `groups.ts`, three media rows (`metropolis/overview`, `team/team-line` and `tidy/walk`), and a `groups` link in the HUD between drive and new.
  It adds no new site key: the site's keys cover only some sections, and a `g` would collide with the github key.
- **S5's test tree** (roadmap manager, 2026-11-07): approved. The 0.3.0 block reads "Two budgets 0.3.0 did not meet", and `release.ts` loses `continues`.
  S5 also takes three fixes from S4's frames:
  - The `.flip` rows mirror, through a `:global()`.
  - The HUD at 390 fades at its right edge, so a link it cuts reads as more to scroll.
  - The Groups copy changes three ways. The "a group" fact goes, since its station-era sentence contradicts 0.5.0's default line and the lead already says what a group is. The changelog's leading "Now" goes from the teammate and group-of-one facts. And "this group" becomes "a group" in close group.
- **Fully up to date** (Aria, 2026-11-07: *"Get the website fully up to date"*). Item 360 stays open after S5 for two things. It moves its quotes to item 361's new wording, and it takes item 362's shots: the City Hall marker, the clinic's list, the action menu, the groups board and the held `e`, with the Glance hotspots re-checked if the hero still changes.
- **The Groups layout once item 362 lands** (roadmap manager, 2026-11-07): approved. Each fact becomes a card, with its media on top at 16:9 and then its title and line, laid out two across on desktop and one on a phone.
  The line's card spans the full width, with the three line-form stills behind a toggle named by the setting's values, default first.
  Clips get controls, a poster and no autoplay.
  A group of one stays text only, since no shot shows one, and a badge borrowed from another shot would claim what it doesn't show.
- **A merge mode for the importer** (roadmap manager, 2026-11-07): `make media-import MERGE=1`. `make media-import` takes only a whole film, and item 362's film is partial, while 0.5.0's full film is no longer on disk. So a pure `merge(existing, partial)` in `tools/media.ts` adds or replaces entries by id, keeps the rest and the views, and refuses a different version. It lists the stills it leaves stale, and prunes nothing in `.media/`.
  `media.json` records each entry's source commit as well as the film's, since a merged catalog comes from more than one.
  0.5.1's re-film imports whole, as usual.
- **Three test trees** (roadmap manager, 2026-11-07): approved. They cover the City Hall hotspot on the film's `hall` anchor, quoting `KindHall`; the Groups section as cards; and Drive's media (`controls/menu`, `menu-rightclick`, `keys` and `clinic`).
  The board card shows `controls/board-rename`, the clip, since renaming is what the board is for. Its still is the poster.
  `controls/hall` and `menu-space` stay unused.
- **The import waits on Aria** (2026-11-07): the merged import is committed in the worktree, unpushed, until she passes 362's contact sheet and uploads the clips with her 1Password.
  After the upload the gate goes fully green, then `make publishable` runs, then the push.
