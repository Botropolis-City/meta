# 139. Sessions with no known folder make a district called ".", and two folders with one name are indistinguishable

**Fixed 2026-10-19 (`96dc535`, r736). Filed 2026-10-19 (r707), noticed during the validation checklist's run against main before 0.2.0. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`63267da`, r729).
Landed: slice 2 (`96dc535`, r736).

On Aria's machine on 2026-10-19 the sidebar's first district was named **"."**, holding two sessions whose record carries no working directory (`botropolis status --all --json` gives them `cwd: ""`): one removed with `claude rm` the day before, and one older.
`filepath.Base("")` is `"."`, so a session the city knows only from the statistics store or a record without a folder lands in a district named after an empty path.
Separately, two districts were both called **botropolis**: `~/workspaces/github/botropolis` (before the 2026-10-15 move) and `~/workspaces/github/botropolis-city/botropolis`; the sidebar, the map's labels and the City Plan show the same name for both.

## The fix

- A session with no known folder belongs to no district on the map; it is still counted in statistics, and if it must be shown, it is in a district named plainly ("folder unknown"), never ".".
- When two districts share a base name, each is labelled with as much of its path as tells them apart (`github/botropolis` and `botropolis-city/botropolis`), everywhere a district is named.

Tests: a session with an empty cwd → it should not make a district named "."; two roots with one base name → each label should differ, and each should end in the shared name.

## Closed

Slice 1 (`63267da`, r729) added `city.DistrictNames`, which labels each root with the fewest trailing folders that no other root ends in, and "folder unknown" for an empty root.
A session with no folder now makes no building, no district and no depot crate.
Names are computed over every root the city knows, hidden ones included, so a label does not change when its twin is hidden.
They name districts on the map, the City Plan, the sidebar and its hidden list, cards, the journal, voyages, the search, and the scripted `district:` and `car:` targets.
Slice 2 (`96dc535`, r736) applies the same names to the power plant's by-district split, which comes from the statistics store.
That split had merged twin roots into one share and named the empty root ".".
The long ranges' district chooser and filter line use the same names, and when the store cannot be read, sessions with no folder still count in the totals.
The tests are `pkg/city/districtnames_test.go` and the twin case in `pkg/ui/ranges_test.go`.

Deviations, for Aria:
- Item 116's breakdown test filed cinders in the store under `/w/cinders`, beside a city session in another folder also named cinders.
  Those are twins, so the fixture now uses the city's own root.
- `botropolis status` and the TUI still print the base of a session's folder, which is "." for a session with no folder.
  That column names a folder, not a district, so it is left as it was.
- No frame was rendered: the change is to labels, and the tests assert them.
