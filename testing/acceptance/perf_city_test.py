import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from stubs import BusyDesk, close_city, executable, fake_desk, path_without, run_in_own_group  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOL = os.path.join(ROOT, 'performance', 'tools', 'perf-city')
DAEMON = '#!/usr/bin/env bash\nsleep 600 &\nwait\n'
REFUSAL = 'a city window is already open'


class PerfCity(unittest.TestCase):
    other_display = None

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.desk = BusyDesk(cls.top)
        sbin = os.path.join(cls.top, 'sbin')
        os.makedirs(sbin)
        executable(os.path.join(sbin, 'botropolisd'), DAEMON)
        cls.daemon = run_daemon(os.path.join(sbin, 'botropolisd'))
        cls.open = cls.desk.open_city(cls.other_display or cls.desk.display)
        env = cls.desk.env(path_without((), os.path.join(cls.top, 'bin'), fake_desk()), PERF_CITY_WINDOW_WAIT='1')
        cls.done = run_in_own_group([TOOL, '--bin', os.path.join(cls.desk.build, 'botropolis'), '--seconds', '1',
                                     '--interval', '1', '--out', os.path.join(cls.top, 'out')], env, 90)

    @classmethod
    def tearDownClass(cls):
        close_city(cls.open)
        close_city(cls.daemon)
        shutil.rmtree(cls.top, ignore_errors=True)


def run_daemon(path):
    return subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


class WhenPerfCityStartsAndAWindowedCityRunsOnAnotherDisplay(PerfCity):
    other_display = ':perf-test-elsewhere'

    def test_it_should_start_its_own_city(self):
        self.assertIn('# city pid', self.done.stderr, self.done.stderr[-2000:])


class WhenPerfCityStartsAndAWindowedCityRunsOnItsOwnDisplay(PerfCity):
    def test_it_should_refuse(self):
        self.assertEqual(self.done.returncode, 1, self.done.stderr[-2000:])

    def test_it_should_say_a_city_window_is_already_open(self):
        self.assertIn(REFUSAL, self.done.stderr)


if __name__ == '__main__':
    unittest.main()
