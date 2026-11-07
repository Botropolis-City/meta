# 360. The website still describes the city of 0.3.0

**Open, in progress since 2026-11-07 in the session "item 360". Filed 2026-11-07 (r1331) at Aria's request. Nobody's call — the content is what shipped; Aria judges the frames.**

Landed: slice 1 (`d18f0c4`, r53).

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
