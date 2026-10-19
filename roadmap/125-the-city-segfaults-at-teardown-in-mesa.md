# 125. The city sometimes segfaults at teardown, inside Mesa

**Open, in progress since 2026-10-18 in the session "item 125". Filed 2026-10-18 (r636), from what item 114 measured. Nobody's call — a defect.**

A headless or `--home` screenshot run sometimes exits with status 139, a segfault, as it shuts down: GLFW's terminate unloads EGL (`dlclose`) while a Mesa gallium thread is still running, inside `RunGame`'s teardown.
Item 114 counted it in 2 or 3 of 60 runs at a load of about 29, and found nine core dumps of `botropolis` on this machine from one afternoon, across several sessions' acceptance runs.
Its A/B showed it predates item 114's changes; Mesa was upgraded to 26.2.5 the day before (2026-10-17), which may be the trigger.
A segfault can run no cleanup, so item 114's sweep of dead owners' private directories is what keeps it from leaking state.

## The fix

Find whether it is ours — a GL object or goroutine still alive at teardown, or GLFW terminated while a frame is in flight — or Mesa's alone, and if ours, quiesce rendering before Ebitengine terminates.
If it is Mesa's, say which version and whether it is reported upstream, and make the tests that hit it report a teardown crash as such rather than as a test failure.

Tests: a headless screenshot run repeated at load should exit 0 every time once the cause is fixed, counted over enough runs to tell 3 in 60 from none.

## Answered while building

- **The cause is ours to fix** (item 125's session, 2026-10-18): Ebitengine terminates GLFW on the main thread, which unloads EGL while the context is still current on the render thread, so Mesa's llvmpipe rasterizers are drawing in code that has just been unmapped; 4 in 60 runs crashed at load, none with llvmpipe's worker threads turned off. The fix keeps the already-loaded GL libraries from being unloaded (`RTLD_NOLOAD|RTLD_NODELETE`, through purego) once the context exists, so teardown cannot unmap them under a running thread. Aria chose not to report it upstream (2026-10-18); the diagnosis and versions stay here.
