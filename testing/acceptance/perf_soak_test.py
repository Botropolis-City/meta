import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from stubs import BusyDesk, executable, path_without, run_in_own_group, snapshot  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOL = os.path.join(ROOT, 'performance', 'tools', 'perf-soak')
DESKTOP = {'i3-msg', 'xprop', 'xset'}
SECONDS = 6
SCALED = {'PERF_SOAK_SETTLE': '1', 'PERF_SOAK_MIN_PHASE': '1'}


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ''


class Soak(unittest.TestCase):
    absent = DESKTOP
    extra_bin = {}
    flags = []

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.desk = BusyDesk(cls.top)
        cls.out = os.path.join(cls.top, 'out')
        cls.before = snapshot(cls.desk.watched)
        cls.env = cls.desk.env(path_without(cls.absent, os.path.join(cls.top, 'bin'), cls.extra_bin),
                               PERF_SOAK_REPO=os.path.join(cls.top, 'not-a-checkout'), **SCALED)
        cls.argv = [TOOL, '--seconds', str(SECONDS), '--hide-after', str(SECONDS // 2), '--interval', '1',
                    '--out', cls.out] + cls.flags + [cls.desk.build]
        cls.run_soak()
        cls.after = snapshot(cls.desk.watched)
        cls.soak = read(os.path.join(cls.out, 'soak.md'))
        cls.busy = read(os.path.join(cls.out, 'busy.txt'))

    @classmethod
    def run_soak(cls):
        cls.done = run_in_own_group(cls.argv, cls.env, 120)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)


class WhenSoakingAStubBuildWithoutADesktop(Soak):
    def test_it_should_run_to_the_end_and_write_its_verdict(self):
        self.assertTrue(self.soak.startswith('# Soak verdict:'), self.done.stderr[-2000:])

    def test_it_should_say_the_window_could_not_be_hidden(self):
        self.assertIn('could not hide the window', self.done.stderr)

    def test_it_should_exit_as_not_a_measurement(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])

    def test_it_should_record_the_scratch_daemons_pid(self):
        self.assertIn('daemon_pid=%s' % self.desk.spied('daemon-pid').strip(), self.busy.splitlines())

    def test_it_should_write_a_row_for_the_citys_visible_phase(self):
        self.assertTrue(any(line.startswith('| city | visible |') for line in self.soak.splitlines()), self.soak)

    def test_it_should_hold_the_demo_for_longer_than_the_run(self):
        argv = self.desk.spied('stager-stage').splitlines()
        hold = argv[argv.index('--hold') + 1]
        self.assertGreater(int(hold.rstrip('s')), SECONDS)

    def test_it_should_record_the_load_at_the_start_and_the_end(self):
        self.assertEqual({line.split('=')[0] for line in self.busy.splitlines() if line.startswith('load_at_')},
                         {'load_at_start', 'load_at_end'})

    def test_and_the_botropolis_checkout_cannot_be_reached_it_should_say_the_landings_went_uncounted(self):
        self.assertIn('landings_during: unchecked', self.soak)

    def test_it_should_name_the_display_it_ran_on(self):
        self.assertIn('display: %s' % os.environ.get('DISPLAY', ''), self.soak)

    def test_it_should_leave_the_callers_state_config_cache_and_data_untouched(self):
        self.assertEqual(self.after, self.before)


class WhenSoakingOnADisplayItIsGiven(Soak):
    flags = ['--display', ':164']

    def test_it_should_open_the_city_on_that_display(self):
        self.assertEqual(self.desk.spied('city-display').strip(), ':164')


class WhenSoakingWithTheHideTurnedOff(Soak):
    flags = ['--no-hide']

    def test_it_should_record_that_it_hid_nothing(self):
        self.assertIn('hide: none', self.soak)

    def test_it_should_not_say_the_window_could_not_be_hidden(self):
        self.assertNotIn('could not hide the window', self.done.stderr)

    def test_it_should_judge_the_visible_phase_alone(self):
        self.assertNotIn('| city | hidden |', self.soak)


ON_DESKTOP = (os.environ.get('PERF_SOAK_ON_DESKTOP') == '1'
              and subprocess.run(['pgrep', '-x', 'i3'], capture_output=True).returncode == 0
              and shutil.which('zenity') is not None)


@unittest.skipUnless(ON_DESKTOP, 'opens a window on the desktop: set PERF_SOAK_ON_DESKTOP=1 on an i3 desktop with zenity')
class WhenSoakingAWindowOnAnI3Desktop(Soak):
    absent = set()

    @classmethod
    def setUpClass(cls):
        cls.window_city = 'exec zenity --info --title perf-soak-test --text "perf-soak test window"\n'
        super().setUpClass()

    @classmethod
    def run_soak(cls):
        executable(os.path.join(cls.desk.build, 'botropolis'), '#!/usr/bin/env bash\necho "FRAME 120 draw 1.0 ms" >&2\n' + cls.window_city)
        super().run_soak()

    def test_it_should_hide_the_window_part_way(self):
        self.assertIn('hidden_at_s: %d' % (SECONDS // 2), self.soak)


if __name__ == '__main__':
    unittest.main()
