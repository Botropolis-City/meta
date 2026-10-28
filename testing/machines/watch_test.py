import contextlib
import importlib.machinery
import importlib.util
import io
import os
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_loader = importlib.machinery.SourceFileLoader('machines_runner', os.path.join(HERE, 'machines'))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
machines = importlib.util.module_from_spec(_spec)
_loader.exec_module(machines)

RUN_ID = 'soak-20261027-114700-3101537'
START = 1_800_000_000.0
POLL = machines.POLL
CEILING_IN = 8 * 3600
NIGHT = 5 * 3600 + 25 * 60


class FakeClock:
    def __init__(self, jumps=None):
        self.wall, self.steady, self.sleeps = START, 0.0, 0
        self.jumps = jumps or {}

    def time(self):
        return self.wall

    def monotonic(self):
        return self.steady

    def sleep(self, seconds):
        self.sleeps += 1
        self.wall += seconds + self.jumps.get(self.sleeps, 0)
        self.steady += seconds


class FakeBucket:
    def __init__(self, clock, answers):
        self.clock, self.answers, self.read_at = clock, list(answers), []

    def get(self, key):
        self.read_at.append(self.clock.time())
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        if isinstance(answer, Exception):
            raise answer
        return answer


class FakeReport:
    def __init__(self, bucket):
        self.bucket, self.run_id, self.last = bucket, RUN_ID, None

    def fetch(self):
        self.last = START
        return True


class Watching(unittest.TestCase):
    jumps = {}
    answers = [None]

    @classmethod
    def setUpClass(cls):
        cls.clock = FakeClock(cls.jumps)
        cls.bucket = FakeBucket(cls.clock, cls.answers)
        cls.ceiling = START + CEILING_IN
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            cls.code = machines.watch(types.SimpleNamespace(max_hours=8.0), FakeReport(cls.bucket), cls.ceiling,
                                      cls.clock)
        cls.said = out.getvalue() + err.getvalue()

    def reads_after_waking(self):
        return [t for t in self.bucket.read_at if t >= self.ceiling]


class WhenTheClockJumpsPastTheCeiling(Watching):
    jumps = {2: CEILING_IN + NIGHT}


class WhenTheClockJumpsPastTheCeilingAndTheBucketHoldsAnEndedSoak(WhenTheClockJumpsPastTheCeiling):
    answers = [None, None, b'0\n']

    def test_it_should_return_the_soaks_exit_code(self):
        self.assertEqual(self.code, 0)

    def test_it_should_read_the_bucket_once_after_waking(self):
        self.assertEqual(len(self.reads_after_waking()), 1, self.bucket.read_at)

    def test_it_should_say_the_soak_ended(self):
        self.assertIn('the soak ended', self.said)

    def test_it_should_not_say_the_soak_was_still_running(self):
        self.assertNotIn('still running', self.said)

    def test_it_should_log_the_sleep_and_how_long_it_lasted(self):
        self.assertIn('slept for 13 h 25 min', self.said)


class WhenTheClockJumpsPastTheCeilingAndTheBucketShowsTheSoakStillRunning(WhenTheClockJumpsPastTheCeiling):
    answers = [None]

    def test_it_should_return_no_exit_code(self):
        self.assertIsNone(self.code)

    def test_it_should_say_the_ceiling_was_reached_with_the_soak_still_running(self):
        self.assertIn('reached its ceiling of 8 hours', self.said)


class WhenTheClockJumpsPastTheCeilingAndTheBucketCannotBeRead(WhenTheClockJumpsPastTheCeiling):
    answers = [None, None, machines.BucketError('503')]

    def test_it_should_return_no_exit_code(self):
        self.assertIsNone(self.code)

    def test_it_should_say_it_could_not_tell_whether_the_soak_ended(self):
        self.assertIn('could not tell whether the soak ended', self.said)

    def test_it_should_not_say_the_soak_was_still_running(self):
        self.assertNotIn('still running', self.said)


class WhenTheClockRunsWithoutAGapAndTheSoakEndsOnTheThirdTurn(Watching):
    answers = [None, None, b'1\n']

    def test_it_should_return_its_exit_code(self):
        self.assertEqual(self.code, 1)

    def test_it_should_log_no_sleep(self):
        self.assertNotIn('slept', self.said)


class WhenMeasuringAGapInTheRunnersClock(unittest.TestCase):
    def test_and_wall_time_moved_hours_more_than_monotonic_it_should_give_the_sleep_in_hours_and_minutes(self):
        self.assertEqual(machines.sleep_gap(NIGHT + 30, 30), '5 h 25 min')

    def test_and_the_two_moved_together_within_a_minute_it_should_give_nothing(self):
        self.assertIsNone(machines.sleep_gap(POLL + 59, POLL))


if __name__ == '__main__':
    unittest.main()
