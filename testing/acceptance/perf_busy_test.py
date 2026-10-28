import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from stubs import DESK, BusyDesk, fake_desk, path_without, run_in_own_group, snapshot  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOL = os.path.join(ROOT, 'performance', 'tools', 'perf-busy-city')
ABSENT = {'i3-msg', 'xprop', 'xset'}


class WhenI3XpropAndXsetAreAbsent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        desk = BusyDesk(cls.top)
        cls.watched = desk.watched
        cls.before = snapshot(cls.watched)
        cls.spy = desk.spy
        cls.out = os.path.join(cls.top, 'out')
        cls.home = desk.home
        env = desk.env(path_without(ABSENT, os.path.join(cls.top, 'bin')))
        cls.done = run_in_own_group([TOOL, '--seconds', '4', '--out', cls.out, desk.build], env, 90)
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


class WhenRunningOnADeskWithAShowAfterTheHide(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        desk = BusyDesk(cls.top)
        out = os.path.join(cls.top, 'out')
        env = desk.env(path_without(set(DESK), os.path.join(cls.top, 'bin'), fake_desk()))
        cls.done = run_in_own_group([TOOL, '--seconds', '6', '--hide-after', '2', '--show-after', '4', '--keep-focus',
                                     '--profile-seconds', '0', '--out', out, desk.build], env, 90)
        try:
            with open(os.path.join(out, 'run', 'env.txt')) as f:
                cls.marks = f.read().splitlines()
        except OSError:
            cls.marks = []

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)

    def test_it_should_record_when_it_showed_the_window_again(self):
        self.assertIn('shown_at_s=4', self.marks, self.done.stderr[-2000:])


class WhenReplayingLooksOnTheBusyDesk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        desk = BusyDesk(cls.top)
        out = os.path.join(cls.top, 'out')
        env = desk.env(path_without(ABSENT, os.path.join(cls.top, 'bin')))
        cls.done = run_in_own_group([TOOL, '--seconds', '4', '--replay-looks', '--profile-seconds', '0',
                                     '--out', out, desk.build], env, 90)
        cls.busy = WhenI3XpropAndXsetAreAbsent.read('busy.txt', out)
        cls.replay = WhenI3XpropAndXsetAreAbsent.read('replay.txt', out)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)

    def test_it_should_record_replay_looks_in_the_run(self):
        self.assertIn('replay=looks', self.busy.splitlines(), self.done.stderr[-2000:])

    def test_it_should_say_it_replayed_looks(self):
        self.assertIn('looks', self.replay)


if __name__ == '__main__':
    unittest.main()
