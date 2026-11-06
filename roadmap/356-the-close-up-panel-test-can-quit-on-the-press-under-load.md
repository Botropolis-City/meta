# 356. The close-up panel's test can see the city quit on the press itself under load

**Fixed 2026-11-06 (`ae557733`, r1274). Filed 2026-11-06 (r1268), from item 350's session watching main under a load of about 50. Nobody's call — a flaky test.**

`pkg/render`'s `TestCloseUpPanel` fails about two runs in three on a loaded machine, in *"when nothing is live"* (`closeup_test.go:61`) and *"when Enter is pressed"* (`:235`), with `regular termination`.
It trips `make land` for any session, whatever it changed.

## Why

Item 291 made a close-up that records and pauses set `Game.closedUp`, which `handleKeys` checks after every tick's keys and leaves through `g.leave()`.
`closeUpWith` (`pkg/render/closeup.go:79`) runs the actor in a goroutine, and the test's recorder returns at once,
so under load the goroutine can set `closedUp` before `handleKeys` (`keys.go:166`) checks it in the same call.
The pressing call itself then returns `ebiten.Termination`, while the test requires no error from the press and expects the exit only on the next one.

## The fix

The test waits for the actor's goroutine and asserts the exit on whichever call sees it, the press or the next, rather than timing the two;
the city's own behaviour, leaving on the tick after a close-up records, is right and stays.

## Fixed

`closingUp` in `closeup_test.go` settles the close-up's actor and takes the exit from whichever frame sees it, the press's own or the next.
The three cases whose actor succeeds at once use it, and the city's own behaviour is unchanged.
A new case, *"when the close-up has finished before the press is answered"*, starts with the close-up already recorded, which is the race won.
It failed on every run under the old pattern and passes under the new one.
`TestCloseUpPanel` then passed 20 runs of 20 at a load of about 30 to 37, and `make land` passed its whole gate with it.
