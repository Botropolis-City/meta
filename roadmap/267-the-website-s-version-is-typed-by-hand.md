# 267. The website's version number is typed by hand, so every release needs a site edit

**Open, in progress since 2026-10-26 in the session "item 267". Filed 2026-10-26 (r1093) at Aria's request. Nobody's call — Aria chose rebuilding on release.**

Aria, 2026-10-26: *"we should update the website so that it dynamically detects and shows the latest version number without having to edit the website"*.

0.3.1 shipped on 2026-10-26 and the site still says 0.3.0 everywhere, because the version lives in three hand-edited places in botropolis.city:

- `src/data/release.ts`, `release.version: "0.3.0"`, which `Release.astro` shows as *new in 0.3.0* along with prose and figures written for that release;
- the media catalog's `version`, which `HudBar.astro` shows as `v0.3.0` and `Hero.astro` as *New in 0.3.0*: that is the version the demo was **filmed** from, which is honestly a different fact from the latest release;
- prose: the index page's description and `Install.astro`'s note on restarting the daemon both name 0.3.0.

`src/data/install.ts` already links `releases/latest/download`, so the download buttons were never stale.

## Two ways, for Aria

1. **Rebuilt on release (recommended).** The site's build reads the latest release from GitHub (`/repos/Botropolis-City/botropolis/releases/latest`) and its section of `CHANGELOG.md` (`release.ts`'s `section()` already cuts one out), and botropolis's release workflow sends a `repository_dispatch` to botropolis.city as its last step, so the site rebuilds and deploys minutes after every release. The page stays static and needs nothing at request time; a build that cannot reach GitHub fails rather than show a guess.
2. **Read at request time.** The Worker serving the site fetches the latest release, cached for some minutes, and rewrites the version into the page with `HTMLRewriter`. Always current, but every page view depends on a GitHub call or its cache, and the rest of the page stays as built.

Either way:

- The **latest version** shows in one place, from one source; the **filmed version** stays labelled as such where it captions the film, so the site never claims a frame came from a build it did not.
- The *new in* section comes from the release's own changelog section, so it is never about the wrong release; the hand-written performance figures for 0.3.0 either name 0.3.0 as the version they measured or move under it.
- The acceptance test (`testing/acceptance/site/page.spec.ts`) holds the page's version to the latest release in a fixture, and fails on any hard-coded version number left in `src/`.

## Answered while building

- **How the site learns of a release** (Aria, 2026-10-26, after the manager's case for it: *"Ok, ya let's do option 1. But we don't need to rebuild hourly. I'm a solo dev and things don't change that often if I'm not working on the project actively."*): option 1, rebuilt on release. botropolis's release workflow dispatches the site's build as its last step, and nothing rebuilds on a schedule; a dispatch that is ever lost is made up by running the site's workflow by hand (`workflow_dispatch`), which the release checklist says to do if the site does not show the new version.
- **The plan's four questions** (manager, 2026-10-26, from the item's own rule that the latest shows in one place and the filmed version is labelled where it captions the film): the HUD shows the latest release, linked to it, and the theatre's lead says *Filmed in v{media.version}*; the three hand-written 0.3.0 cards stay, under a subsection named for 0.3.0, since dropping content is Aria's; the dispatch is `workflow_dispatch` of `site.yml` with a fine-grained token holding only Actions read and write on botropolis.city (narrower than `repository_dispatch`, which needs Contents write, and the same path as the manual fallback), stored as botropolis's Actions secret `SITE_DISPATCH_TOKEN`, which Aria creates; and the manual-fallback line goes in `botropolis/RELEASING.md`'s after-release steps.
