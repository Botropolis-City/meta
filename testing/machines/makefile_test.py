import os
import shutil
import subprocess
import tempfile
import unittest

MAKEFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Makefile')


def dry_run(*assignments):
    with tempfile.TemporaryDirectory() as work:
        shutil.copy(MAKEFILE, work)
        env = {k: v for k, v in os.environ.items()
               if k not in ('KEEP_ON_FAILURE', 'MAKEFLAGS', 'MFLAGS', 'MAKELEVEL')}
        return subprocess.run(['make', '-n', '-C', work, 'run-wayland', 'SCRIPT=x', *assignments],
                              env=env, capture_output=True, text=True)


class WhenKeepOnFailureIsUnset(unittest.TestCase):
    def test_it_should_not_pass_keep_on_failure(self):
        self.assertNotIn('--keep-on-failure', dry_run().stdout)


class WhenKeepOnFailureIsZero(unittest.TestCase):
    def test_it_should_not_pass_keep_on_failure(self):
        self.assertNotIn('--keep-on-failure', dry_run('KEEP_ON_FAILURE=0').stdout)


class WhenKeepOnFailureIsOne(unittest.TestCase):
    def test_it_should_pass_keep_on_failure(self):
        self.assertIn('--keep-on-failure', dry_run('KEEP_ON_FAILURE=1').stdout)


class WhenKeepOnFailureIsAnythingElse(unittest.TestCase):
    VALUES = ('yes', 'true', '2', 'no', '0 1')

    @classmethod
    def setUpClass(cls):
        cls.runs = {v: dry_run(f'KEEP_ON_FAILURE={v}') for v in cls.VALUES}

    def test_it_should_exit_non_zero(self):
        for value, run in self.runs.items():
            with self.subTest(value=value):
                self.assertNotEqual(run.returncode, 0)

    def test_it_should_name_one_and_zero_in_its_error(self):
        for value, run in self.runs.items():
            with self.subTest(value=value):
                self.assertRegex(run.stderr, r'KEEP_ON_FAILURE=1.*KEEP_ON_FAILURE=0')


if __name__ == '__main__':
    unittest.main()
