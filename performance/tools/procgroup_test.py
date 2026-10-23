import os
import shutil
import signal
import subprocess
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, 'lib', 'procgroup.sh')

FIXTURE = '''#!/usr/bin/env bash
set -euo pipefail
. "{lib}"
procgroup_lead "$@"
cleanup() {{ sleep 0.3; echo cleaned >>"$DIR/log"; }}
procgroup_on_exit cleanup
sleep 300 &
echo $! >"$DIR/sleep"
echo "$$ $(ps -o pgid= -p $$ | tr -d ' ')" >"$DIR/ids.tmp" && mv "$DIR/ids.tmp" "$DIR/ids"
case "$1" in
wait) wait ;;
exit) exit "$2" ;;
esac
'''


def eventually(check, within=5.0):
    deadline = time.monotonic() + within
    while not check():
        if time.monotonic() > deadline:
            return False
        time.sleep(0.05)
    return True


def group_is_gone(pgid):
    try:
        os.killpg(pgid, 0)
        return False
    except ProcessLookupError:
        return True


class ScriptFixture(unittest.TestCase):
    """Starts a script that sources the lib and backgrounds a sleep, then calls act()."""

    ARGS = ['wait']
    NEW_SESSION = True

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.script = os.path.join(cls.dir, 'fixture')
        with open(cls.script, 'w') as f:
            f.write(FIXTURE.format(lib=LIB))
        os.chmod(cls.script, 0o755)
        cls.ids = None
        cls.proc = subprocess.Popen([cls.script] + cls.ARGS, env=dict(os.environ, DIR=cls.dir),
                                    start_new_session=cls.NEW_SESSION,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if eventually(lambda: os.path.exists(os.path.join(cls.dir, 'ids'))):
            with open(os.path.join(cls.dir, 'ids')) as f:
                pid, pgid = f.read().split()
            cls.ids = (int(pid), int(pgid))
        cls.act()
        cls.returncode = cls.proc.wait(timeout=15)

    @classmethod
    def act(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        if cls.proc.poll() is None:
            cls.proc.kill()
            cls.proc.wait()
        if cls.ids and cls.ids[0] == cls.ids[1]:
            try:
                os.killpg(cls.ids[1], signal.SIGKILL)
            except ProcessLookupError:
                pass
        cls.kill_own_sleep()
        shutil.rmtree(cls.dir, ignore_errors=True)

    @classmethod
    def kill_own_sleep(cls):
        """Kill the fixture's sleep if it is still alive and still carries this fixture's DIR, as when the lib is broken."""
        try:
            with open(os.path.join(cls.dir, 'sleep')) as f:
                pid = int(f.read())
            with open('/proc/%d/environ' % pid, 'rb') as f:
                mine = ('DIR=' + cls.dir).encode() in f.read().split(b'\0')
            if mine:
                os.kill(pid, signal.SIGKILL)
        except (OSError, ValueError):
            pass

    def cleaned(self):
        path = os.path.join(self.dir, 'log')
        if not os.path.exists(path):
            return False
        with open(path) as f:
            return f.read() == 'cleaned\n'


class WhenAScriptLeadsItsGroupAndIsSentTerm(ScriptFixture):
    @classmethod
    def act(cls):
        cls.proc.send_signal(signal.SIGTERM)

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(eventually(lambda: group_is_gone(self.proc.pid)))

    def test_it_should_run_its_cleanup(self):
        self.assertTrue(self.cleaned())

    def test_it_should_exit_as_terminated(self):
        self.assertEqual(self.returncode, 143)


class WhenAScriptLeadsItsGroupAndExitsNormally(ScriptFixture):
    ARGS = ['exit', '0']

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(eventually(lambda: group_is_gone(self.proc.pid)))

    def test_it_should_run_its_cleanup(self):
        self.assertTrue(self.cleaned())

    def test_it_should_exit_with_its_own_status(self):
        self.assertEqual(self.returncode, 0)


class WhenAScriptIsStartedInsideAnotherGroup(ScriptFixture):
    ARGS = ['exit', '7']
    NEW_SESSION = False

    def test_it_should_lead_a_group_of_its_own(self):
        self.assertEqual(self.ids[0], self.ids[1])

    def test_it_should_leave_the_group_it_was_started_in(self):
        self.assertNotEqual(self.ids[1], os.getpgrp())

    def test_it_should_pass_its_exit_status_through(self):
        self.assertEqual(self.returncode, 7)

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(eventually(lambda: group_is_gone(self.ids[1])))


class WhenAScriptIsStartedInsideAnotherGroupAndItsLauncherIsSentTerm(ScriptFixture):
    NEW_SESSION = False

    @classmethod
    def act(cls):
        cls.proc.send_signal(signal.SIGTERM)
        cls.proc.wait(timeout=15)
        cls.cleaned_when_launcher_exited = cls.cleaned(cls)

    def test_it_should_not_exit_before_the_scripts_cleanup_has_run(self):
        self.assertTrue(self.cleaned_when_launcher_exited)

    def test_it_should_exit_as_terminated(self):
        self.assertEqual(self.returncode, 143)

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(eventually(lambda: group_is_gone(self.ids[1])))

    def test_it_should_run_its_cleanup(self):
        self.assertTrue(eventually(self.cleaned))


class WhenAScriptIsStartedInsideAnotherGroupAndItsLauncherIsKilled(ScriptFixture):
    NEW_SESSION = False

    @classmethod
    def act(cls):
        cls.proc.kill()

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(eventually(lambda: group_is_gone(self.ids[1])))

    def test_it_should_run_its_cleanup(self):
        self.assertTrue(eventually(self.cleaned))


if __name__ == '__main__':
    unittest.main()
