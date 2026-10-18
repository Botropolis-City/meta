# 119. The website credits nobody for its art

**Open. Filed 2026-10-18 (r628), from the art audit Aria asked for. Nobody's call — Aria asked for it.**

Aria, 2026-10-18: *"Make sure that for anything we pulled from an asset pack we have followed their licensing and attributed and thanked them."*

Every frame on botropolis.city is mostly [Kenney](https://kenney.nl)'s work: the roads, trees, cars, trains, boats and water towers, and, in frames filmed before item 109, the buildings too.
The site never says so.
Its footer, `botropolis.city/src/components/Footer.astro`, carries one line besides the email address: *"Botropolis is not affiliated with Anthropic."*
A search of `botropolis.city/src` for `kenney` finds nothing.

CC0 asks for no credit, so this is not a licence breach.
It is a thank-you that is missing from the one page most people see, while the app's README already gives it.
Kenney's terms, from [kenney.nl/support](https://kenney.nl/support): credit "Kenney" if you like, and do not use the studio's logo.

## The fix

A line in the footer's `.small` row, beside the affiliation line, saying the city is drawn from Kenney's CC0 kits, rendered in Blender, with a link to kenney.nl and to [kenney.nl/donate](https://kenney.nl/donate).
Text only, and no Kenney logo.
Optionally name the typefaces too, Inter and JetBrains Mono, both OFL; web use asks for no credit, so that part is courtesy.

`botropolis.city/testing/acceptance/site/page.spec.ts` is where the footer's text would be pinned.

## Done when

The footer names Kenney with a link to kenney.nl, a test fails if the line is removed, and the site is deployed with it.
