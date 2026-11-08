# 370. botropolis.city has no `make publishable` guard

**Open. Filed 2026-11-07 (r1343), found by item 369's session. Nobody's call — a gap in a guard.**

Depends on: 369

meta and botropolis each run `make publishable` before a push: it sweeps the history for the employer's names where the list exists, and refuses any advertised ref outside the history being published.
botropolis.city is public too, and it has no such target. Nothing on its `main` mentions `publishable`, `ls-remote` or `is-ancestor`.
Its remote advertises `refs/pull/1` to `7/head` and four branches that were never deleted (`feat/media-bucket`, `fix/bot-fight-mode`, `fix/email-routing-settings` and `fix/verify-sigpipe`), and nothing has ever swept any of them.

## The fix

Give botropolis.city the same guard as meta, with [item 369](369-make-publishable-refuses-forever-on-a-merged-pull-request.md)'s handling of pull-request refs. Sweep the history and every advertised ref once.
Then deleting the four stale branches is Aria's call, since they are public. Ask before deleting any.
Add the step to the site's CLAUDE.md and to the push routine that item sessions follow there.
