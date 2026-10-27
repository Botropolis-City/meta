import hashlib
import os
import signal
import subprocess
import textwrap

DAEMON = textwrap.dedent('''\
    #!/usr/bin/env bash
    printf '%s\\n' "$@" >"$PERF_BUSY_TEST_SPY/argv"
    printf '%s\\n' "$HOME" >"$PERF_BUSY_TEST_SPY/home"
    echo $$ >"$PERF_BUSY_TEST_SPY/daemon-pid"
    [[ -L "$HOME/.claude/projects/-p/a.jsonl" ]] && echo linked >"$PERF_BUSY_TEST_SPY/history"
    for d in "${XDG_STATE_HOME:-$HOME/.local/state}" "${XDG_CONFIG_HOME:-$HOME/.config}" \\
             "${XDG_CACHE_HOME:-$HOME/.cache}" "${XDG_DATA_HOME:-$HOME/.local/share}"; do
        mkdir -p "$d/botropolis" && echo written >"$d/botropolis/stats.db"
    done
    sock=""
    while [[ $# -gt 0 ]]; do [[ "$1" == --socket ]] && sock="$2"; shift; done
    python3 -I -c 'import socket,sys,time
    s=socket.socket(socket.AF_UNIX); s.bind(sys.argv[1]); s.listen(); time.sleep(600)' "$sock" &
    wait
    ''')

CITY = textwrap.dedent('''\
    #!/usr/bin/env bash
    [[ -n "${PERF_BUSY_TEST_SPY:-}" ]] && echo "${DISPLAY:-}" >"$PERF_BUSY_TEST_SPY/city-display"
    [[ -n "${PERF_BUSY_TEST_SPY:-}" ]] && echo $$ >"$PERF_BUSY_TEST_SPY/city-pid"
    echo "FRAME 120 draw 1.0 ms" >&2
    sleep 600 &
    wait
    ''')

STAGER = textwrap.dedent('''\
    #!/usr/bin/env bash
    cmd=$1; shift; home=""
    [[ -n "${PERF_BUSY_TEST_SPY:-}" ]] && printf '%s\\n' "$@" >"$PERF_BUSY_TEST_SPY/stager-$cmd"
    while [[ $# -gt 0 ]]; do [[ "$1" == --home ]] && home="$2"; shift; done
    [[ "$cmd" == stage ]] || exit 0
    mkdir -p "$home/.claude/projects/-demo" "$home/.claude/sessions"
    for n in 1 2; do
        printf '{}\\n' >"$home/.claude/projects/-demo/s$n.jsonl"
        printf '{"sessionId": "s%s", "cwd": "/demo"}' "$n" >"$home/.claude/sessions/$n.json"
    done
    ''')

DESK = ('xprop', 'xwininfo', 'i3-msg', 'xset')
DESK_WINDOW = 4242
DESK_TOOL = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys
    name, args = os.path.basename(sys.argv[0]), sys.argv[1:]
    spy = os.environ['PERF_BUSY_TEST_SPY']
    broken = set(filter(None, os.environ.get('FAKE_DESK_BROKEN', '').split(',')))
    with open(os.path.join(spy, 'desk'), 'a') as f:
        f.write(json.dumps([name] + args) + '\\n')
    def read(n):
        try:
            with open(os.path.join(spy, n)) as f:
                return f.read().strip()
        except OSError:
            return ''
    def write(n, v):
        with open(os.path.join(spy, n), 'w') as f:
            f.write(v)
    if name in broken:
        sys.exit(1)
    if name == 'xset':
        print('  Monitor is On')
    elif name == 'xprop' and '-id' in args:
        print('_NET_WM_PID(CARDINAL) = %s' % ('1' if 'no-window' in broken else read('city-pid')))
    elif name == 'xwininfo' and '-id' in args:
        print('  Width: 1920\\n  Height: 1080\\n  Map State: %s'
              % ('IsUnMapped' if read('window') == 'hidden' else 'IsViewable'))
    elif name == 'i3-msg' and args[:2] == ['-t', 'get_tree']:
        print(json.dumps({'nodes': [{'window': WINDOW, 'nodes': []}] if read('city-pid') else []}))
    elif name == 'i3-msg' and args[:2] == ['-t', 'get_version']:
        print(json.dumps({'human_readable': '4.24'}))
    elif name == 'i3-msg':
        command, ok = ' '.join(args), True
        if 'move scratchpad' in command:
            ok = 'no-hide' not in broken
            if ok:
                write('window', 'hidden')
        elif 'scratchpad show' in command and 'no-show' not in broken:
            write('window', 'shown')
        print(json.dumps([{'success': ok}], separators=(',', ':')))
    ''').replace('WINDOW', str(DESK_WINDOW))


def fake_desk(without=()):
    """xprop, xwininfo, i3-msg and xset that find, hide and show the stub city's window, less any named."""
    return {name: DESK_TOOL for name in DESK if name not in without}


def executable(path, text):
    with open(path, 'w') as f:
        f.write(text)
    os.chmod(path, 0o755)


def snapshot(roots):
    seen = {}
    for root in roots:
        seen[root] = None if not os.path.lexists(root) else []
        for d, dirs, files in os.walk(root):
            dirs.sort()
            for name in sorted(dirs + files):
                path = os.path.join(d, name)
                st = os.lstat(path)
                digest = ''
                if os.path.isfile(path) and not os.path.islink(path):
                    with open(path, 'rb') as f:
                        digest = hashlib.sha256(f.read()).hexdigest()
                seen[root].append((os.path.relpath(path, root), st.st_size, st.st_mtime_ns, digest))
    return seen


def run_in_own_group(argv, env, timeout):
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(argv, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return subprocess.CompletedProcess(argv, -1, '', 'timed out')


def path_without(names, into, extra=None):
    os.makedirs(into)
    for name, text in (extra or {}).items():
        executable(os.path.join(into, name), text)
    for d in os.environ['PATH'].split(os.pathsep):
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            src = os.path.join(d, name)
            dst = os.path.join(into, name)
            if name in names or os.path.lexists(dst) or not os.access(src, os.X_OK) or os.path.isdir(src):
                continue
            os.symlink(src, dst)
    return into


class BusyDesk:
    """A stub build, demo stager, real-looking home and XDG directories under one temporary top."""

    def __init__(self, top):
        self.top = top
        self.build = os.path.join(top, 'build')
        os.makedirs(self.build)
        executable(os.path.join(self.build, 'botropolisd'), DAEMON)
        executable(os.path.join(self.build, 'botropolis'), CITY)
        self.stager = os.path.join(top, 'botropolis-demo')
        executable(self.stager, STAGER)
        self.home = os.path.join(top, 'home')
        os.makedirs(os.path.join(self.home, '.claude', 'projects', '-p'))
        os.makedirs(os.path.join(self.home, '.claude', 'sessions'))
        with open(os.path.join(self.home, '.claude', 'projects', '-p', 'a.jsonl'), 'w') as f:
            f.write('{}\n')
        self.real = {name: os.path.join(top, name) for name in ('state', 'config', 'cache', 'data')}
        for d in self.real.values():
            os.makedirs(os.path.join(d, 'botropolis'))
            with open(os.path.join(d, 'botropolis', 'stats.db'), 'w') as f:
                f.write('real\n')
        self.watched = list(self.real.values()) + [os.path.join(self.home, d) for d in ('.local', '.config', '.cache', '.claude')]
        self.spy = os.path.join(top, 'spy')
        os.makedirs(self.spy)

    def env(self, path, **extra):
        return dict(os.environ,
                    PATH=path,
                    HOME=self.home,
                    XDG_STATE_HOME=self.real['state'],
                    XDG_CONFIG_HOME=self.real['config'],
                    XDG_CACHE_HOME=self.real['cache'],
                    XDG_DATA_HOME=self.real['data'],
                    PERF_BUSY_TEST_SPY=self.spy,
                    BOTROPOLIS_DEMO=self.stager,
                    PERF_BUSY_SETTLE='0',
                    PERF_BUSY_REPLAY_FROM='1',
                    PERF_BUSY_PPROF_WAIT='1',
                    **extra)

    def spied(self, name):
        try:
            with open(os.path.join(self.spy, name)) as f:
                return f.read()
        except OSError:
            return ''
