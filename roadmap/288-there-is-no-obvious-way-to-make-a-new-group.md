# 288. There is no obvious way to make a new group, and *move to group* offers none

**Done 2026-10-26 (`d8686cf`, r1132). Filed 2026-10-26 (r1123), from Aria's use of 0.3.2. Nobody's call — Aria said what she wants.**

Aria, 2026-10-26: *"it should be really obvious how to create a new group. And it should be available in the move to group menu."*

## Where it stands

A group made by hand exists only through the New session panel's group name (`pkg/render/newsession.go`, stored in `pkg/commands/city.go` under `group.NewGroupID`).
The card's *move to group* opens a picker (`pkg/render/move.go`) listing every group and *no group*, with no way to make one.

## The fix

1. The picker's first row is **new group…**: choosing it asks for a name inline, in the picker, and enter makes the group and moves the session into it, through the same path the New session panel uses.
2. The picker's title and the help say so, and the card's hint for *move to group* reads "Moves this session into a group, or into a new one you name."
3. An empty name or a name already taken is refused in words in the picker.
4. Tests: choosing *new group…*, typing a name and pressing enter makes the group with the session in it; the new group is listed next time the picker opens; an empty or taken name is refused and nothing changes; esc while naming returns to the list.
5. A frame of the picker with *new group…* chosen and a name being typed, for Aria.

## Closed

The *move to group* picker starts with **new group…**: choosing it asks for a name in the picker, enter makes the group and moves the session into it, an empty name or one a group already has (ignoring case) is refused in words, and esc returns to the list.
Typing goes through a `textinput.Composer`, held by item 289's keyboard guard.
The group is stored by `Memory.WithNewGroup`, which New session now shares, inside `Actor.move`'s single load-then-save, so item 286's lock covers it.
The card's hint reads "Moves this session into a group, or into a new one you name.", the picker's title says so, and the reference's *city hall* entry says how a group is made.
Tests: `TestMoveToGroup` (`pkg/render`), `TestActorMove` (`pkg/commands`, including `group.Detect` listing the new group), `TestKinds`, `TestBuildingGroup`.

Deviation, agreed with the manager: a card offers *move to group* whenever its session is not resting, even with no groups at all; before, it needed one group to exist, so the first group could never be made from a card.
A clip's script keys now type into text fields, as `--keys` does.
Frames for Aria: `botropolis/docs/screenshots/r1130-item-288-new-group-list.png` and `r1130-item-288-new-group-naming.png`.
