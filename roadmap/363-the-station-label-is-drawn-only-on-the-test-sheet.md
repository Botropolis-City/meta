# 363. The station label is drawn only on the render test sheet

**Open. Filed 2026-11-07 (r1332), left over from [item 361](361-the-station-glossary-entry-outlived-the-stations.md). Nobody's call — dead code.**

`queueStationLabel` in `botropolis/pkg/render/maplabels.go` (line 49) names a line beside its first station. Since 0.5.0 a group's line has no stations, and its only caller is the render test sheet, `pkg/render/sheetfront.go` line 73.

## The fix

Remove it and its call on the sheet. If the sheet's frame then changes, re-render the sheet, and check that nothing else names a station label, such as a test or a label budget in `maplabels.go`.
