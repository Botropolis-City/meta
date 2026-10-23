import hashlib
import os
import shutil
import signal
import subprocess
import tempfile
import textwrap
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOL = os.path.join(ROOT, 'performance', 'tools', 'perf-busy-city')
ABSENT = {'i3-msg', 'xprop', 'xset'}

DAEMON = textwrap.dedent('''\
    #!/usr/bin/env bash
    printf '%s\\n' "$@" >"$PERF_BUSY_TEST_SPY/argv"
    printf '%s\\n' "$HOME" >"$PERF_BUSY_TEST_SPY/home"
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
    sleep 600 &
    wait
    ''')

STAGER = textwrap.dedent('''\
    #!/usr/bin/env bash
    cmd=$1; shift; home=""
    while [[ $# -gt 0 ]]; do [[ "$1" == --home ]] && home="$2"; shift; done
    [[ "$cmd" == stage ]] || exit 0
    mkdir -p "$home/.claude/projects/-demo" "$home/.claude/sessions"
    for n in 1 2; do
        printf '{}\\n' >"$home/.claude/projects/-demo/s$n.jsonl"
        printf '{"sessionId": "s%s", "cwd": "/demo"}' "$n" >"$home/.claude/sessions/$n.json"
    done
    ''')


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


def path_without(names, into):
    os.makedirs(into)
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


class WhenI3XpropAndXsetAreAbsent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        top = cls.top
        build = os.path.join(top, 'build')
        os.makedirs(build)
        executable(os.path.join(build, 'botropolisd'), DAEMON)
        executable(os.path.join(build, 'botropolis'), CITY)
        stager = os.path.join(top, 'botropolis-demo')
        executable(stager, STAGER)
        home = os.path.join(top, 'home')
        os.makedirs(os.path.join(home, '.claude', 'projects', '-p'))
        os.makedirs(os.path.join(home, '.claude', 'sessions'))
        with open(os.path.join(home, '.claude', 'projects', '-p', 'a.jsonl'), 'w') as f:
            f.write('{}\n')
        real = {name: os.path.join(top, name) for name in ('state', 'config', 'cache', 'data')}
        for d in real.values():
            os.makedirs(os.path.join(d, 'botropolis'))
            with open(os.path.join(d, 'botropolis', 'stats.db'), 'w') as f:
                f.write('real\n')
        cls.watched = list(real.values()) + [os.path.join(home, '.local'), os.path.join(home, '.config'),
                                             os.path.join(home, '.cache'), os.path.join(home, '.claude')]
        cls.before = snapshot(cls.watched)
        cls.spy = os.path.join(top, 'spy')
        os.makedirs(cls.spy)
        cls.out = os.path.join(top, 'out')
        env = dict(os.environ,
                   PATH=path_without(ABSENT, os.path.join(top, 'bin')),
                   HOME=home,
                   XDG_STATE_HOME=real['state'],
                   XDG_CONFIG_HOME=real['config'],
                   XDG_CACHE_HOME=real['cache'],
                   XDG_DATA_HOME=real['data'],
                   PERF_BUSY_TEST_SPY=cls.spy,
                   BOTROPOLIS_DEMO=stager,
                   PERF_BUSY_SETTLE='0',
                   PERF_BUSY_REPLAY_FROM='1',
                   PERF_BUSY_PPROF_WAIT='1')
        cls.home = home
        cls.done = run_in_own_group([TOOL, '--seconds', '4', '--out', cls.out, build], env, 90)
        cls.after = snapshot(cls.watched)
        cls.busy = cls.read('busy.txt')
        cls.replay = cls.read('replay.txt')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)

    @classmethod
    def read(cls, name, under=None):
        try:
            with open(os.path.join(under or cls.out, name)) as f:
                return f.read()
        except OSError:
            return ''

    def test_it_should_still_run_to_the_end(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr[-2000:])

    def test_it_should_say_the_focus_hand_back_was_skipped(self):
        self.assertIn('focus hand-back skipped', self.done.stderr)

    def test_it_should_say_the_monitor_check_was_skipped(self):
        self.assertIn('monitor check skipped', self.done.stderr)

    def test_it_should_say_the_cpu_profile_was_skipped(self):
        self.assertIn('CPU profile skipped', self.done.stderr)

    def test_it_should_record_every_skip_in_the_run(self):
        self.assertEqual({line.split('=')[0] for line in self.busy.splitlines() if 'skipped' in line or 'unchecked' in line},
                         {'focus_handback', 'monitor', 'profile'})

    def test_it_should_still_replay_the_writers(self):
        self.assertIn('appended', self.replay)

    def test_it_should_not_point_the_daemon_at_a_home_with_a_flag(self):
        self.assertNotIn('--home', self.read('argv', self.spy).splitlines())

    def test_it_should_run_the_daemon_with_its_home_set_to_the_scratch_home(self):
        self.assertNotIn(self.read('home', self.spy).strip(), ('', self.home))

    def test_it_should_give_the_daemon_the_history_through_its_scratch_home(self):
        self.assertEqual(self.read('history', self.spy).strip(), 'linked')

    def test_it_should_leave_the_callers_state_config_cache_and_data_untouched(self):
        self.assertEqual(self.after, self.before)


if __name__ == '__main__':
    unittest.main()
