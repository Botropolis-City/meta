# 265. What has to be true before 1.0.0 is written nowhere

**Open. Filed 2026-10-26 (r1093) at Aria's request. Aria's call — which criteria make the bar.**

Aria asked on 2026-10-26, *"how far are we from 1.0.0?"*, and the answer could only be an estimate, because the bar is in nobody's file.
She then asked for this item, for the manager to draft the criteria and for her to rule on them.

What exists already:

- [Item 149](149-what-1-0-0-promises.md) wrote down what 1.0.0 **promises**, the public surface that cannot break without a 2.0.0, and `make version-check` holds it from 1.0.0 on.
- [Item 167](167-the-cli-has-spread-and-ships-no-man-pages.md) and [item 154](154-a-fresh-eyes-audit-of-the-city.md) were filed "on the road to 1.0.0".
- `botropolis/RELEASING.md` says how a release is cut, and Aria's rule until 1.0.0: the middle digit for breaking changes, the last for features and fixes.

What is missing is the **bar**: what must be true of a build before it is called 1.0.0.

## A draft for Aria to rule on

Each is a candidate, with how it would be checked:

1. **The soak passes.** An 8-hour soak of the release build stays within the growth budget (item 164, item 245's runner).
2. **Every performance budget is met** in `make test-performance` and on Aria's screen, with no item open against a budget. As of r1089 the suite is met; item 212's dry pass is not.
3. **The validation checklist passes**, A1 to A6 by Aria and the rest scripted, against the release build.
4. **The platforms it claims work**: Linux on X11 and Wayland, and macOS, each verified on a machine (items 95 and 96, through item 245's machines), or the claim narrowed to what was verified.
5. **CI is green on every platform for a week**, with no test known to be flaky left open.
6. **No open defect a user would hit**, every item filed as a defect closed or ruled acceptable for 1.0.0 by name.
7. **The packages install clean** on a machine that is not the builder's, from every channel (AUR, APT, RPM, Homebrew), item 263's kind of failure caught by CI.
8. **The documentation matches the build**: the man pages, `--help`, the website and the demo film, re-filmed from the release build.
9. **Which vision items are in 1.0.0**, by number, and which wait for after it. That is Aria's alone, and it is the line most of the rest depends on.

When Aria has ruled, the bar goes into `botropolis/RELEASING.md` as a 1.0.0 checklist, and each criterion that is not met yet becomes, or names, an open item.
