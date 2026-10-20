# 172. The key reference leaves out `u`, and shows five keys at their defaults however they are set

**Open, in progress since 2026-10-20 in the session "item 172". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

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
