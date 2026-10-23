import os
import shutil
import signal
import subprocess
import tempfile
import time
import unittest

from procgroup import run_in_group


def group_is_gone(pgid, within=5.0):
    deadline = time.monotonic() + within
    while True:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(0.05)


class GroupFixture(unittest.TestCase):
    """Runs SCRIPT once with run_in_group; the script writes its own pid, its group's id, to $DIR/pid."""

    SCRIPT = 'exit 0'
    TIMEOUT = 10
    KW = {}

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.error = None
        cls.result = None
        cls.started = time.monotonic()
        try:
            cls.result = run_in_group(['sh', '-c', 'echo $$ >"$DIR/pid"; ' + cls.SCRIPT],
                                      timeout=cls.TIMEOUT, env=dict(os.environ, DIR=cls.dir), **cls.KW)
        except BaseException as e:  # noqa: B036 - the interrupted case raises KeyboardInterrupt
            cls.error = e
        cls.elapsed = time.monotonic() - cls.started
        with open(os.path.join(cls.dir, 'pid')) as f:
            cls.pgid = int(f.read())

    @classmethod
    def tearDownClass(cls):
        try:
            os.killpg(cls.pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        shutil.rmtree(cls.dir, ignore_errors=True)


class WhenACommandFinishesInTime(GroupFixture):
    SCRIPT = 'echo out; echo err >&2; exit 3'
    KW = {'capture_output': True, 'text': True}

    def test_it_should_return_its_exit_code(self):
        self.assertEqual(self.result.returncode, 3)

    def test_it_should_return_its_stdout(self):
        self.assertEqual(self.result.stdout, 'out\n')

    def test_it_should_return_its_stderr(self):
        self.assertEqual(self.result.stderr, 'err\n')


class WhenACommandFinishesInTimeAndLeavesABackgroundChild(GroupFixture):
    SCRIPT = 'sleep 300 >/dev/null 2>&1 & exit 0'

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(group_is_gone(self.pgid))


class WhenACommandFailsAndCheckIsSet(GroupFixture):
    SCRIPT = 'exit 4'
    KW = {'check': True}

    def test_it_should_raise_called_process_error(self):
        self.assertIsInstance(self.error, subprocess.CalledProcessError)


class WhenACommandOutlivesItsTimeout(GroupFixture):
    SCRIPT = 'echo started; sleep 300 & wait'
    TIMEOUT = 0.5
    KW = {'capture_output': True, 'text': True}

    def test_it_should_raise_timeout_expired(self):
        self.assertIsInstance(self.error, subprocess.TimeoutExpired)

    def test_it_should_attach_what_it_printed(self):
        self.assertEqual(self.error.output, 'started\n')

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(group_is_gone(self.pgid, within=0))


class WhenACommandOutlivesItsTimeoutAndIgnoresTerm(GroupFixture):
    SCRIPT = "trap '' TERM; sleep 300 & wait"
    TIMEOUT = 0.5
    KW = {'grace': 0.3}

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(group_is_gone(self.pgid, within=0))


class WhenTheCallerIsInterrupted(GroupFixture):
    SCRIPT = 'sleep 300 & wait'
    TIMEOUT = 60

    @classmethod
    def setUpClass(cls):
        def interrupt(*_):
            raise KeyboardInterrupt
        previous = signal.signal(signal.SIGALRM, interrupt)
        signal.setitimer(signal.ITIMER_REAL, 0.5)
        try:
            super().setUpClass()
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)

    def test_it_should_let_the_interrupt_through(self):
        self.assertIsInstance(self.error, KeyboardInterrupt)

    def test_it_should_leave_no_process_in_its_group(self):
        self.assertTrue(group_is_gone(self.pgid, within=0))

    def test_it_should_not_wait_out_the_timeout(self):
        self.assertLess(self.elapsed, 10)


if __name__ == '__main__':
    unittest.main()
