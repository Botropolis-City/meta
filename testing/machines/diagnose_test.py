import importlib.machinery
import importlib.util
import io
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_loader = importlib.machinery.SourceFileLoader('machines_runner', os.path.join(HERE, 'machines'))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
machines = importlib.util.module_from_spec(_spec)
_loader.exec_module(machines)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(text)


class Collecting(unittest.TestCase):
    preflight_ran = True

    @classmethod
    def setUpClass(cls):
        cls.box = tempfile.mkdtemp()
        setup_log = os.path.join(cls.box, 'root', 'setup.log')
        preflight = os.path.join(cls.box, 'soak', 'run', 'preflight')
        out = os.path.join(cls.box, 'soak', 'run', 'out')
        write(setup_log, 'setup: done\n')
        write(os.path.join(out, 'dri.txt'), 'renderer: stub\n')
        if cls.preflight_ran:
            write(os.path.join(preflight, 'perf-city.err'), '# city pid 42\n')
            write(os.path.join(preflight, 'run', 'env.txt'), 'window_at_start=unknown\n')
            write(os.path.join(preflight, 'run', 'city.log'), 'panic: no GL context\n')
        command = machines.diagnose_command([setup_log, os.path.join(cls.box, 'not', 'there.log')],
                                            [('preflight', preflight), ('out', out)])
        done = subprocess.run(['bash', '-c', command], capture_output=True)
        cls.returncode = done.returncode
        cls.names = set()
        with tarfile.open(fileobj=io.BytesIO(done.stdout), mode='r:gz') as tar:
            cls.names = {os.path.normpath(n) for n in tar.getnames()}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.box, ignore_errors=True)


class WhenCollectingFromABoxWhosePreflightFailed(Collecting):
    def test_it_should_hold_the_preflights_env_txt(self):
        self.assertIn('preflight/run/env.txt', self.names)

    def test_it_should_hold_the_preflights_city_log(self):
        self.assertIn('preflight/run/city.log', self.names)

    def test_it_should_hold_the_preflights_perf_city_err(self):
        self.assertIn('preflight/perf-city.err', self.names)

    def test_it_should_hold_the_soaks_out_directory(self):
        self.assertIn('out/dri.txt', self.names)

    def test_it_should_still_hold_the_set_up_log(self):
        self.assertIn('setup.log', self.names)

    def test_it_should_exit_zero(self):
        self.assertEqual(self.returncode, 0)


class WhenCollectingFromABoxWhosePreflightNeverRan(Collecting):
    preflight_ran = False

    def test_it_should_still_hold_the_set_up_log(self):
        self.assertIn('setup.log', self.names)

    def test_it_should_hold_no_preflight_directory(self):
        self.assertNotIn('preflight', self.names)


class WhenReadingTheRunnersDiagnosticsCommand(unittest.TestCase):
    def test_it_should_collect_the_directory_the_preflight_writes_to(self):
        self.assertIn(machines.PREFLIGHT, machines.DIAGNOSE)


if __name__ == '__main__':
    unittest.main()
