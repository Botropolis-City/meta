import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from stubs import DESK, DESK_WINDOW, BusyDesk, executable, fake_desk, path_without, run_in_own_group, snapshot  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOL = os.path.join(ROOT, 'performance', 'tools', 'perf-soak')
SECONDS = 6
SCALED = {'PERF_SOAK_SETTLE': '1', 'PERF_SOAK_MIN_PHASE': '1', 'PERF_SOAK_PREFLIGHT_SECONDS': str(SECONDS),
          'PERF_CITY_WINDOW_WAIT': '2'}


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ''


class Soak(unittest.TestCase):
    absent = set(DESK)
    desk_tools = DESK
    broken = ''
    flags = []

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.desk = BusyDesk(cls.top)
        cls.out = os.path.join(cls.top, 'out')
        cls.before = snapshot(cls.desk.watched)
        extra = fake_desk(without=set(DESK) - set(cls.desk_tools))
        cls.env = cls.desk.env(path_without(cls.absent,os.path.join(cls.top, 'bin'), extra),
                               PERF_SOAK_REPO=os.path.join(cls.top, 'not-a-checkout'), FAKE_DESK_BROKEN=cls.broken,
                               **SCALED)
        cls.argv = cls.command()
        cls.run_soak()
        cls.after = snapshot(cls.desk.watched)
        cls.soak = read(os.path.join(cls.out, 'soak.md'))
        cls.busy = read(os.path.join(cls.out, 'busy.txt'))

    @classmethod
    def command(cls):
        return [TOOL, '--seconds', str(SECONDS), '--hide-after', str(SECONDS // 2), '--interval', '1',
                '--out', cls.out] + cls.flags + [cls.desk.build]

    @classmethod
    def run_soak(cls):
        cls.done = run_in_own_group(cls.argv, cls.env, 120)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)

    def marks(self):
        return read(os.path.join(self.out, 'run', 'env.txt'))

    def desk_calls(self):
        return [json.loads(line) for line in self.desk.spied('desk').splitlines()]

    def i3_commands(self):
        return [' '.join(c[1:]) for c in self.desk_calls() if c[0] == 'i3-msg' and c[1:2] != ['-t']]


class WhenSoakingAStubBuildOnADesk(Soak):
    def test_it_should_run_to_the_end_and_write_its_verdict(self):
        self.assertTrue(self.soak.startswith('# Soak verdict:'), self.done.stderr[-2000:])

    def test_it_should_hide_the_window_part_way(self):
        self.assertIn('hidden_at_s: %d' % (SECONDS // 2), self.soak)

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


class WhenSoakingAndTheWindowCannotBeHidden(Soak):
    broken = 'no-hide'

    def test_it_should_say_the_window_could_not_be_hidden(self):
        self.assertIn('could not hide the window', self.done.stderr)

    def test_it_should_exit_as_not_a_measurement(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])


class WhenSoakingOnADisplayItIsGiven(Soak):
    flags = ['--display', ':164']

    def test_it_should_open_the_city_on_that_display(self):
        self.assertEqual(self.desk.spied('city-display').strip(), ':164')


class WhenSoakingWithTheHideTurnedOff(Soak):
    desk_tools = ()
    flags = ['--no-hide']

    def test_it_should_run_to_the_end_without_a_desk(self):
        self.assertTrue(self.soak.startswith('# Soak verdict:'), self.done.stderr[-2000:])

    def test_it_should_record_that_it_hid_nothing(self):
        self.assertIn('hide: none', self.soak)

    def test_it_should_not_say_the_window_could_not_be_hidden(self):
        self.assertNotIn('could not hide the window', self.done.stderr)

    def test_it_should_judge_the_visible_phase_alone(self):
        self.assertNotIn('| city | hidden |', self.soak)


class Refusing:
    tool = ''

    def test_it_should_exit_as_not_a_measurement(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])

    def test_it_should_name_the_tool(self):
        self.assertIn(self.tool, self.done.stderr)

    def test_it_should_open_no_city(self):
        self.assertEqual(self.desk.spied('city-pid'), '')


class Preflight(Soak):
    @classmethod
    def command(cls):
        return [TOOL, '--preflight', '--out', cls.out, cls.desk.build]


for _tool in DESK:
    _name = _tool.replace('-', '').capitalize()
    for _kind, _base in (('Soaking', Soak), ('Preflighting', Preflight)):
        _missing = 'When%sAndAToolIsMissing_%s' % (_kind, _name)
        globals()[_missing] = type(_missing, (Refusing, _base), {'tool': _tool, 'desk_tools': tuple(t for t in DESK if t != _tool)})
        _failing = 'When%sAndAToolFailsToRun_%s' % (_kind, _name)
        globals()[_failing] = type(_failing, (Refusing, _base), {'tool': _tool, 'broken': _tool})
del _tool, _name, _kind, _base, _missing, _failing


class WhenPreflightingOnADeskWithEveryTool(Preflight):
    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr[-2000:])

    def test_it_should_hide_the_citys_window(self):
        self.assertIn('[id=%d] move scratchpad' % DESK_WINDOW, self.i3_commands())

    def test_it_should_show_it_again_after_the_hide(self):
        commands = self.i3_commands()
        self.assertGreater(commands.index('[id=%d] scratchpad show' % DESK_WINDOW),
                           commands.index('[id=%d] move scratchpad' % DESK_WINDOW), commands)

    def test_it_should_start_no_soak(self):
        self.assertEqual(self.soak, '')

    def test_it_should_say_it_passed(self):
        self.assertIn('pre-flight passed', self.done.stdout + self.done.stderr)

    def test_it_should_record_how_long_the_window_took_to_appear(self):
        self.assertRegex(self.marks(), r'(?m)^window_found_after_s=[0-9.]+$')


class WhenPreflightingAndTheWindowCannotBeFound(Preflight):
    broken = 'no-window'

    def test_it_should_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])

    def test_it_should_say_the_window_was_not_found(self):
        self.assertIn("the city's window was not found", self.done.stderr)

    def test_it_should_say_the_city_was_still_running(self):
        self.assertIn('the city was still running', self.done.stderr)

    def test_it_should_quote_the_end_of_the_citys_log(self):
        self.assertIn('FRAME 120 draw 1.0 ms', self.done.stderr)

    def test_it_should_record_that_the_city_was_running_at_the_timeout(self):
        self.assertIn('city_running_at_window_timeout=yes', self.marks().splitlines())

    def test_it_should_record_each_window_and_its_pid(self):
        self.assertIn('%d _NET_WM_PID(CARDINAL) = 1' % DESK_WINDOW, read(os.path.join(self.out, 'run', 'windows.txt')))


class WhenPreflightingAndTheCityExitsAtOnce(Preflight):
    broken = 'city-exits'

    def test_it_should_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])

    def test_it_should_say_the_city_had_exited(self):
        self.assertIn('the city had exited', self.done.stderr)

    def test_it_should_quote_the_end_of_the_citys_log(self):
        self.assertIn('the stub city could not open a window', self.done.stderr)

    def test_it_should_record_that_the_city_was_not_running(self):
        self.assertIn('city_running_at_window_timeout=no', self.marks().splitlines())


class WhenPreflightingAndTheWindowDoesNotHide(Preflight):
    broken = 'no-hide'

    def test_it_should_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])

    def test_it_should_say_it_could_not_hide_the_window(self):
        self.assertIn('could not hide the window', self.done.stderr)


class WhenPreflightingAndTheWindowDoesNotShowAgain(Preflight):
    broken = 'no-show'

    def test_it_should_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr[-2000:])

    def test_it_should_say_it_could_not_show_the_window(self):
        self.assertIn('could not show the window', self.done.stderr)


ON_DESKTOP = (os.environ.get('PERF_SOAK_ON_DESKTOP') == '1'
              and subprocess.run(['pgrep', '-x', 'i3'], capture_output=True).returncode == 0
              and shutil.which('zenity') is not None)


@unittest.skipUnless(ON_DESKTOP, 'opens a window on the desktop: set PERF_SOAK_ON_DESKTOP=1 on an i3 desktop with zenity')
class WhenSoakingAWindowOnAnI3Desktop(Soak):
    absent = set()
    desk_tools = ()

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
