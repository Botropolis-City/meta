# 125. The city sometimes segfaults at teardown, inside Mesa

**Fixed 2026-10-18 (`5a99911`, r655). Filed 2026-10-18 (r636), from what item 114 measured. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`5a99911`, r655).

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

## The diagnosis, for an upstream report

Versions: Ebitengine v2.10.2 and its pure-Go GLFW port (`internal/glfw`), purego v0.11.0, Mesa 26.2.5 (Arch `1:26.2.5-1`), llvmpipe under Xvfb, GLES 3.0 over EGL through glvnd.

- The core dumps, symbolized with `eu-stack` and Arch's debuginfod: the main thread is in `dlclose` → `_dl_close_worker` → `munmap`, called from `terminateEGL` in Ebitengine's GLFW port; at the same moment two or more llvmpipe rasterizer threads are inside `thread_function` → `rasterize_scene` → `lp_rast_linear_tile` → `shade_quads`, drawing the last frame, and the one that faults is executing code that was just unmapped.
- Why they are still alive: Ebitengine keeps the GL context current on its render thread (`graphicscommand.LoopRenderThread`) and runs `glfw.Terminate` on the main thread.
  `graphicscommand.Terminate` only flushes the command queue; it neither waits for the GPU nor releases the context.
  EGL defers destroying a context that is current on another thread, so `eglDestroyContext` and `eglTerminate` never destroy llvmpipe's screen or join its threads, and GLFW then unloads the library under them.
- Why it is rare: only when the last frame's rasterization outlasts the main thread's path from the last `Update` to `dlclose`, which load makes likelier.
- The interrupt cases crash the same way: a SIGTERM ends the loop with a frame in flight too.

## Measured

Each run was a `--home` screenshot run on a display of its own, so no X loss is counted.

- Unfixed: 4 in 60 at load about 47, 1 in 120 at load about 50 (the acceptance soak's red); 5 in 180.
- With `LP_NUM_THREADS=0`, no llvmpipe worker threads: 0 in 60.
- With the hold: 0 in 120 (a spike), then 0 in 360 across three runs of `make soak-teardown`, at load 50 to 70.
  At the unfixed 5 in 180, 0 in 480 by luck has a probability of about 1 in 700,000.

## What landed

`pkg/glhold` reopens each GL library that is already loaded, at the city's first update, with `RTLD_NOLOAD|RTLD_NODELETE`, through purego, since the build is `CGO_ENABLED=0`; nothing it names is loaded if it was not.
It names the EGL, GLES and GLX libraries and Mesa's vendor libraries, and `libgallium` is held through those, which name it as a dependency, so its versioned file name is never needed.
Linux and FreeBSD hold; elsewhere it does nothing.
The city's own cleanup after `RunGame` is unchanged.

The tests: `TestHold`, `TestGameHoldsGLOnce`, `TestHoldKeepsLibraryMapped` (a library held stays mapped after its last handle closes; one not loaded stays unloaded), and `TestTeardownSoak`, opt-in through `make soak-teardown` or `BOTROPOLIS_SOAK=1` because it takes minutes.
Mutated red: dropping NOLOAD fails the unit and integration tests; dropping NODELETE fails only the unit test, because the hold's open handle alone also keeps the library mapped, so the two are belt and braces and either prevents the crash.

## Found on the way, not fixed here

- **Two of the 360 fixed runs exited 1 with `gamepad: Open failed: interrupted system call`.**
  Ebitengine v2.10.2 opens every `/dev/input/event*` at startup (`internal/gamepad/gamepad_linux.go`, `openGamepad`), tolerates `EACCES`, `EPERM` and `ENOENT`, and returns any other error from the game loop,
  so an `open` interrupted under load, by Go's own preemption signal most likely, ends the city.
  It reads the host's devices, so it is not specific to Xvfb.
  It keeps `make soak-teardown` from passing outright; it is not the teardown crash.

## Closed

Fixed in `5a99911` (r655): the cause was ours, Ebitengine's teardown order, and the city now keeps the GL libraries it uses loaded until it exits, so GLFW's `dlclose` cannot unmap Mesa's code under its running threads.
The proof is the soak: 0 segfaults in 480 runs on the fixed code, against 5 in 180 before, each run on a display of its own; the tests are listed under *What landed*.
It is not Mesa's alone, so nothing is reported upstream, and Aria chose not to report Ebitengine's part (2026-10-18); the diagnosis above is written to be filed as it stands.

**For Aria, a deviation from "Tests":** the opt-in `make soak-teardown` asks for exit 0 every time, and it does not yet pass outright.
Its two exit-1s in 360 runs are the gamepad `EINTR` under *Found on the way*, a different defect that the manager is filing as its own item, so the soak's "exit 0 every time" waits on that item, not on this one.
Also found on the way, and filed by the manager beside it: `gofmt -l` flags `botropolis/pkg/render/shore_test.go` on main, though `make lint` is green.
