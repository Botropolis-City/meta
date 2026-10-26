import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from bucket import FakeBucket  # noqa: E402
from stubs import executable, run_in_own_group  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DETACHED = os.path.join(ROOT, 'testing', 'machines', 'soak', 'detached')
WRITE_ID, WRITE_SECRET = 'soak-box-write', 'write-s3cr3t'
RUN_ID = 'soak-20261026-040100-4242'

PERF_SOAK = textwrap.dedent('''\
    #!/usr/bin/env bash
    out=$1
    echo partial >"$out/soak.md"
    sleep 1.5
    echo verdict >"$out/soak.md"
    exit "${SOAK_EXIT:-0}"
    ''')


class TheBoxAlone(unittest.TestCase):
    """The box's half of the soak, run here as the box runs it, with no laptop watching."""

    bucket_options = {}
    soak_exit = '0'

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.out = os.path.join(cls.top, 'out')
        os.makedirs(cls.out)
        soak = os.path.join(cls.top, 'perf-soak')
        executable(soak, PERF_SOAK)
        cls.bucket = FakeBucket({WRITE_ID: WRITE_SECRET}, **cls.bucket_options)
        cls.env_file = os.path.join(cls.top, 'bucket.env')
        with open(cls.env_file, 'w') as f:
            f.write('BUCKET_URL=%s\nBUCKET_ID=%s\nBUCKET_SECRET=%s\n' % (cls.bucket.url, WRITE_ID, WRITE_SECRET))
        os.chmod(cls.env_file, 0o600)
        env = dict(os.environ, SOAK_EXIT=cls.soak_exit)
        cls.done = run_in_own_group(['python3', '-I', DETACHED, '--env', cls.env_file, '--run-id', RUN_ID,
                                     '--every', '0.3', '--out', cls.out, '--', soak, cls.out], env, 60)

    @classmethod
    def tearDownClass(cls):
        cls.bucket.close()
        shutil.rmtree(cls.top, ignore_errors=True)

    def puts(self, suffix):
        return self.bucket.sent('PUT', suffix)

    def uploaded_report(self):
        with tarfile.open(fileobj=io.BytesIO(self.bucket.objects[RUN_ID + '/report.tar.gz']), mode='r:gz') as tar:
            return tar.extractfile('soak.md').read().decode()


class WhenTheBoxRunsTheSoakWithNoLaptop(TheBoxAlone):
    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_upload_the_report_while_the_soak_runs(self):
        self.assertGreaterEqual(len(self.puts('/report.tar.gz')), 2, self.bucket.requests)

    def test_it_should_upload_the_report_at_the_end(self):
        self.assertEqual(self.uploaded_report(), 'verdict\n')

    def test_it_should_upload_the_exit_code(self):
        self.assertEqual(self.bucket.objects.get(RUN_ID + '/exit'), b'0\n')

    def test_it_should_upload_the_exit_code_after_the_last_report(self):
        keys = [r['key'] for r in self.bucket.requests if r['method'] == 'PUT']
        self.assertEqual(keys[-1], RUN_ID + '/exit', keys)

    def test_it_should_sign_every_upload_with_the_write_key_from_its_file(self):
        self.assertEqual({r['key_id'] for r in self.bucket.requests}, {WRITE_ID})

    def test_it_should_leave_the_exit_code_beside_the_report_for_a_fetch_over_ssh(self):
        with open(os.path.join(self.out, 'perf-soak.exit')) as f:
            self.assertEqual(f.read(), '0\n')


class WhenTheBoxRunsTheSoakAndItFails(TheBoxAlone):
    soak_exit = '1'

    def test_it_should_upload_its_exit_code(self):
        self.assertEqual(self.bucket.objects.get(RUN_ID + '/exit'), b'1\n')


class WhenTheBoxRunsTheSoakAndTheBucketRefusesAnUpload(TheBoxAlone):
    bucket_options = {'refuse_puts': 1}

    def test_it_should_keep_the_soak_running_to_its_end(self):
        self.assertEqual(self.bucket.objects.get(RUN_ID + '/exit'), b'0\n')

    def test_it_should_upload_the_report_at_the_next_turn(self):
        self.assertEqual(self.uploaded_report(), 'verdict\n')


class WhenAskingTheBoxsWrapperForHelp(unittest.TestCase):
    def test_it_should_exit_zero(self):
        done = subprocess.run(['python3', '-I', DETACHED, '--help'], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == '__main__':
    unittest.main()
