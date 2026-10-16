import os
import subprocess
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class WhenTheDocumentationIsChecked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = subprocess.run([os.path.join(ROOT, 'tools', 'check-docs')],
                                    capture_output=True, text=True, cwd=ROOT)

    def test_it_should_find_nothing_wrong(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)


if __name__ == '__main__':
    unittest.main()
