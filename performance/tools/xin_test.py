import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
import xin  # noqa: E402

XIN = os.path.join(HERE, 'lib', 'xin.py')


class WhenGatingADisplay(unittest.TestCase):
    def test_and_it_may_be_someones_screen_it_should_refuse(self):
        for display in ('', ':0', ':0.0'):
            with self.subTest('when the display is %r and there is no box marker, it should refuse' % display):
                self.assertIsNotNone(xin.refusal(display, box=False, asked_screen=False))

    def test_and_the_box_marker_exists_it_should_allow_its_display(self):
        self.assertIsNone(xin.refusal(':0', box=True, asked_screen=False))

    def test_and_aria_was_asked_for_the_screen_it_should_allow_it(self):
        self.assertIsNone(xin.refusal(':0', box=False, asked_screen=True))

    def test_and_the_display_is_a_private_one_it_should_allow_it(self):
        self.assertIsNone(xin.refusal(':99', box=False, asked_screen=False))


class WhenRunAgainstAScreenItMayNotTouch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        env = dict(os.environ, DISPLAY='', PERF_XIN_BOX_MARK=os.path.join(cls.top, 'no-marker'))
        cls.done = subprocess.run([sys.executable, '-I', XIN, 'key', 'a'], env=env, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)

    def test_it_should_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_say_it_refuses_the_display(self):
        self.assertIn("xin.py refuses display ''", self.done.stderr)


class WhenConvertingAnXImageRow(unittest.TestCase):
    def test_it_should_turn_bgrx_into_rgb(self):
        self.assertEqual(xin.bgrx_to_rgb(b'\x01\x02\x03\x00\x04\x05\x06\x00', 2), b'\x03\x02\x01\x06\x05\x04')


class WhenWritingAFrame(unittest.TestCase):
    ROWS = [b'\xff\x00\x00\x00\xff\x00', b'\x00\x00\xff\xff\xff\xff']

    def setUp(self):
        self.png = xin.png(2, 2, self.ROWS)

    def test_it_should_start_with_the_png_signature(self):
        self.assertEqual(self.png[:8], b'\x89PNG\r\n\x1a\n')

    def test_it_should_hold_each_row_unfiltered(self):
        start = self.png.index(b'IDAT') + 4
        length = int.from_bytes(self.png[start - 8:start - 4], 'big')
        self.assertEqual(zlib.decompress(self.png[start:start + length]), b'\x00' + self.ROWS[0] + b'\x00' + self.ROWS[1])

    def test_it_should_give_the_mean_luminance(self):
        self.assertAlmostEqual(xin.mean_luma(2, self.ROWS), (0.2126 * 255 + 0.7152 * 255 + 0.0722 * 255 + 255) / 4)


class WhenPerfFitzoomDrivesTheScreen(unittest.TestCase):
    def test_it_should_say_it_was_asked_for_the_screen_on_every_xin_call(self):
        with open(os.path.join(HERE, 'perf-fitzoom')) as f:
            calls = [line for line in f if 'xin.py' in line and not line.lstrip().startswith('#')]
        self.assertTrue(calls and all('--asked-screen' in line for line in calls), calls)


if __name__ == '__main__':
    unittest.main()
