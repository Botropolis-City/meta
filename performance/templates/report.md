# <What was measured>, <YYYY-MM-DD>

**Rig:** <CPU, cores, RAM, GPU that draws, display size, window manager>; never a hostname.
**Builds:** <version and rN of each build measured, and how each was built or installed>.
**History on disk:** <transcripts, MiB, touched in the last hour, projects> (from `env.txt`).
**Runs:** <which of the four runs in method.md, how long each was, the interval>.

## Findings

One line per finding, most expensive first, each with the number that shows it and the run it came from.

1. <finding>: <number> (<run>).

## Daemon

| build | CPU mean | CPU p95 | Private_Dirty last | slope MiB/min | read MiB/s | write MiB/s | sample |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

## City

| build | state | frames drawn | ms/frame | CPU mean | Private_Dirty last | slope MiB/min | GPU MiB | Go live heap MB | sample |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | visible | | | | | | | | |
| | hidden | | | | | | | | |

## What it does not show

What the runs could not separate, what was skipped, and why.
A skipped check written down is a check someone can still run; one left out reads as a pass.

## Reproduce

```sh
<the exact commands, from the meta repository's root>
```
