# 328. The second night holds 6–8 MiB more heap than the first, on every quiet run since the light-cycle check landed

**Fixed 2026-11-03 (`ee58d18`, r1251). Filed 2026-11-03 (r1227), from 0.3.5's release gate. Nobody's call for the diagnosis; Aria's for the target, if the check should judge later nights.**

`TestLightCycleGivesItsMemoryBack` (item 318, 600 districts, night → day → night → day, heap less the records' slack) fails its second night on every quiet run since it landed: r1217 +6 MiB, r1227 +8 and +7, against 4; the second day passes (+3 to +4) and Ebitengine's images stay flat at 87 MiB.
It also fails on GitHub's runner (+8.0, the 0.3.5 dry run), so it is the city, not a machine.
Nothing in 0.3.5's range caused it: the bisect's baseline, the commit that landed the check, fails the same way.
Item 318's seven-phase run at r1210 (raw heap 153 / 160 / 160 / 162 / 161 / 160 / 160) showed nights at 160, 162 and 160: evidence of a one-time second-night step, not a ratchet, but two nights cannot tell the two apart.

## The fix

1. Find what the second night allocates that the first did not (a heap profile at each night's settled point, diffed), and release or pre-size it so the second night costs what the first did.
2. Run the check to three nights so a step and a ratchet read differently; whether the check then judges the third night against the second is a change of target, Aria's call.
3. Until it is fixed, `make test-performance` is red on the reference machine for every run, which hides the next regression.

## Diagnosis, 2026-11-03

The second night's +8 MiB is Ebitengine's per-queue uniform scratch (`graphicscommand.(*uint32sBuffer)`), a high-water mark, not anything the city keeps: heap profiles every 5 s at r1230 put the whole night-1 → night-2 difference in that buffer (6 / 14 / 10 MiB at night 1 / night 2 / day 2), with records, vertices and buildings flat.
Every draw call takes 46+ dwords of uniforms from its queue's buffer before Ebitengine checks whether it can merge the call (ebiten v2.10, their issue #2601); the buffer grows to a power of two and never shrinks, headless flushes pool two or more queues, and each grows when it takes a nightfall frame of about 45k calls.
Bounded at about queues × 8 MiB, which fits item 318's three-night run.

**The fix, approved:** the still draws runs of same-source, same-blend commands as one `DrawTriangles32` each (`pkg/render/ink.go`, `stillframe.go`), so a nightfall frame issues several times fewer calls and the scratch stays under the 4 MiB margin; `TestStillDrawCalls` asserts calls ≤ runs, and the light-cycle check runs seven phases with the third night logged, not judged.

## Closed (item session, 2026-11-03)

Fixed in the city: `ee58d18` (r1251) plays the standing city a run at a time, `476797f` (r1252) runs the light cycle to a third night and logs each phase's load, `e970568` (r1253) drops the guards on Ebitengine's deprecated options, and `9482930` adds the changelog entry.
Runs take colour-matrix draws too, since a viewed city drains its sprites through one matrix and those were a third of the calls.
A frame composing the whole standing city at the acceptance's zoom goes from 9,683 calls to 1,651, and from about 3.0 MiB of uniforms to under 1 MiB.
Measured in the city itself: once each light switch, one or two such frames ran, and when two shared a flush, a queue's buffer went from 4 to 8 MiB.
Whether two did depended on timing, which is how r1233's run read +1 without the fix.
After the fix the pooled queue holds 2 MiB from start to finish.

`TestStillDrawCalls` was red first (193 calls against 167 runs) and is green; `TestTheStillCityMatchesTheCityDrawnDirectly` passes by day and night, and failed (7,635 pixels) with one corner of a quad left unsnapped.
Six seven-phase runs passed, three before a crash lost the first commits and three after rebuilding them.
Heap less slack across night 1 / day 1 / night 2 / day 2 / night 3 / day 3, at loads of 3.4 to 10.8:
99/99/99/99/99/99, 100/99/99/99/100/99, 99/99/99/100/99/99, 99/99/99/99/100/99, 99/100/99/99/99/100 and 100/99/99/99/100/99 MiB.
The third night is logged and not judged; whether it joins the judgement is the performance manager's call.
