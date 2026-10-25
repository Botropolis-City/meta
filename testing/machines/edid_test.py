import shutil
import subprocess
import sys
import unittest

from edid import edid_1080p


class WhenMakingTheForcedEDID(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edid = edid_1080p()
        cls.timing = cls.edid[54:72]

    def test_it_should_be_one_128_byte_block(self):
        self.assertEqual(len(self.edid), 128)

    def test_it_should_start_with_the_edid_header(self):
        self.assertEqual(self.edid[:8], bytes([0, 255, 255, 255, 255, 255, 255, 0]))

    def test_it_should_sum_to_zero_modulo_256(self):
        self.assertEqual(sum(self.edid) % 256, 0)

    def test_it_should_be_edid_version_1_3(self):
        self.assertEqual((self.edid[18], self.edid[19]), (1, 3))

    def test_it_should_have_no_extension_blocks(self):
        self.assertEqual(self.edid[126], 0)

    def test_and_the_preferred_timing_it_should_clock_148_5_mhz(self):
        self.assertEqual(self.timing[0] | self.timing[1] << 8, 14850)

    def test_and_the_preferred_timing_it_should_be_1920_wide(self):
        self.assertEqual(self.timing[2] | (self.timing[4] >> 4) << 8, 1920)

    def test_and_the_preferred_timing_it_should_be_1080_high(self):
        self.assertEqual(self.timing[5] | (self.timing[7] >> 4) << 8, 1080)

    def test_and_the_preferred_timing_it_should_refresh_at_60_hz(self):
        h_total = 1920 + (self.timing[3] | (self.timing[4] & 0x0F) << 8)
        v_total = 1080 + (self.timing[6] | (self.timing[7] & 0x0F) << 8)
        self.assertAlmostEqual(14850 * 10000 / (h_total * v_total), 60.0, places=3)

    def test_it_should_pass_edid_decodes_conformity_check(self):
        if not shutil.which('edid-decode'):
            sys.stderr.write('\n  SKIPPED %s: edid-decode is not installed\n' % self.id())
            self.skipTest('edid-decode is not installed')
        done = subprocess.run(['edid-decode', '-c', '-'], input=self.edid, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stdout.decode()[-800:])


if __name__ == '__main__':
    unittest.main()
