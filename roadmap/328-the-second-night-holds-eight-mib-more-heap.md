# 328. The second night holds 6–8 MiB more heap than the first, on every quiet run since the light-cycle check landed

**Open. Filed 2026-11-03 (r1227), from 0.3.5's release gate. Nobody's call for the diagnosis; Aria's for the target, if the check should judge later nights.**

`TestLightCycleGivesItsMemoryBack` (item 318, 600 districts, night → day → night → day, heap less the records' slack) fails its second night on every quiet run since it landed: r1217 +6 MiB, r1227 +8 and +7, against 4; the second day passes (+3 to +4) and Ebitengine's images stay flat at 87 MiB.
It also fails on GitHub's runner (+8.0, the 0.3.5 dry run), so it is the city, not a machine.
Nothing in 0.3.5's range caused it: the bisect's baseline, the commit that landed the check, fails the same way.
Item 318's seven-phase run at r1210 (raw heap 153 / 160 / 160 / 162 / 161 / 160 / 160) showed nights at 160, 162 and 160: evidence of a one-time second-night step, not a ratchet, but two nights cannot tell the two apart.

## The fix

1. Find what the second night allocates that the first did not (a heap profile at each night's settled point, diffed), and release or pre-size it so the second night costs what the first did.
2. Run the check to three nights so a step and a ratchet read differently; whether the check then judges the third night against the second is a change of target, Aria's call.
3. Until it is fixed, `make test-performance` is red on the reference machine for every run, which hides the next regression.
