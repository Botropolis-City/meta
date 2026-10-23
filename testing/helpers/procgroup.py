"""Run a command in a process group of its own, and never leave any of that group behind.

subprocess.run's timeout kills only the direct child: anything that child started
(a backgrounded daemon, a foreground `go build` in a subshell) is orphaned and
reparented to the nearest subreaper. run_in_group starts the command as the
leader of a new session and, on timeout, on an exception in the caller, and
after the command exits, signals the whole group: SIGTERM, a grace period,
then SIGKILL. The group's id is the pid of a process this module started, so it
never signals a pid it looked up.
"""

import os
import signal
import subprocess
import time


def _signal_group(pgid, sig):
    try:
        os.killpg(pgid, sig)
        return True
    except ProcessLookupError:
        return False


def _group_alive(pgid):
    return _signal_group(pgid, 0)


def _stop_group(pgid, grace):
    if not _signal_group(pgid, signal.SIGTERM):
        return
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        if not _group_alive(pgid):
            return
        time.sleep(0.05)
    _signal_group(pgid, signal.SIGKILL)


def run_in_group(cmd, timeout=None, input=None, check=False, capture_output=False, grace=2.0, **kw):
    """Like subprocess.run, but the command and everything it starts share a process group that is stopped whole."""
    if capture_output:
        kw['stdout'] = subprocess.PIPE
        kw['stderr'] = subprocess.PIPE
    if input is not None:
        kw['stdin'] = subprocess.PIPE
    kw.pop('start_new_session', None)
    with subprocess.Popen(cmd, start_new_session=True, **kw) as proc:
        pgid = proc.pid
        try:
            stdout, stderr = proc.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            _stop_group(pgid, grace)
            stdout, stderr = proc.communicate()
            raise subprocess.TimeoutExpired(proc.args, timeout, output=stdout, stderr=stderr) from None
        except BaseException:
            _stop_group(pgid, grace)
            proc.communicate()
            raise
        _stop_group(pgid, grace)
    result = subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)
    if check:
        result.check_returncode()
    return result
