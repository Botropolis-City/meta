# 168. Share the city as a picture, GIF or clip, in a sharing mode

**Open, in progress since 2026-10-20 in the session "item 168". Filed 2026-10-20 (r786) at Aria's request, from item 167's analysis. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`6be1962`, r801).
Landed: slice 2 (`9a85987`, r809).

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
