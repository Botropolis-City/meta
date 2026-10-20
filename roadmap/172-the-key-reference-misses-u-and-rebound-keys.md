# 172. The key reference leaves out `u`, and shows five keys at their defaults however they are set

**Fixed 2026-10-20 (`f246ebd`, r797). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

The reference (`?` or F1) is built from `bindings` in `botropolis/pkg/render/keys.go`, through `helpKeys`.

- **`u` is not in it.**
  `u` fetches the plan's usage again and sends the launch down the river, the launch's own caption says *"that you asked for with u"*, and with `usage_refresh = manual`, the default, it is the only way to get the figures.
  It is in neither the reference's list of keys nor the footer; only the launch's own description mentions it.
- **Five rebindable keys are always shown at their defaults.**
  `helpKeys` spells the City Plan, labels and finder chords as configured, but not triage (`--triage_key`, shown as `w`), the journal (`--journal_key`, `shift+w`), the stream (`--stream_key`, `l`), New session (`--new_session_key`, `shift+n`) or explain (`--explain_key`, `hold e`).
  Rebind any of them and the reference names a key that does something else or nothing.

The fix adds `u` to `bindings` and routes the other five through `findChords()` the way `planBinding` and `labelsBinding` are.
A test that rebinds every configurable key and asserts each appears in `helpKeys` under its new name would keep the next one from being missed.

## Closed

Fixed in `f246ebd` (r797).
The reference lists `u` beside the power breakdown,
and `helpKeys` now takes every rebindable row from one table — the City Plan, labels, triage, the journal, the stream, New session and explain — so each is spelled as configured, with explain as `hold <key>`.
`pkg/render/helpkeys_test.go` sets every field of `config.Chords` to its own chord by reflection and asserts each appears in the reference,
so a chord added later without a row fails it.
Defaults read exactly as before.
No frame: it is a text change in the reference panel, and the manager agreed none was needed.
