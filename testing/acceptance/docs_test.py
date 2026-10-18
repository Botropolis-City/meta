import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def check_docs(tree):
    return subprocess.run([os.path.join(tree, 'tools', 'check-docs')],
                          capture_output=True, text=True, cwd=tree)


class WhenTheDocumentationIsChecked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = check_docs(ROOT)

    def test_it_should_find_nothing_wrong(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)


class WhenTwoItemsShareANumber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = tempfile.mkdtemp()
        tracked = subprocess.run(['git', 'ls-files'], capture_output=True, text=True,
                                 cwd=ROOT, check=True).stdout.split('\n')
        for f in filter(None, tracked):
            src = os.path.join(ROOT, f)
            if not os.path.isfile(src):
                continue
            dst = os.path.join(cls.tree, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        first = sorted(p for p in os.listdir(os.path.join(cls.tree, 'roadmap'))
                       if p[:3].isdigit())[0]
        shutil.copy2(os.path.join(cls.tree, 'roadmap', first),
                     os.path.join(cls.tree, 'roadmap', first[:4] + 'a-second-file-with-the-same-number.md'))
        cls.result = check_docs(cls.tree)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tree)

    def test_it_should_name_the_number_used_twice(self):
        self.assertRegex(self.result.stdout, r'item \d{3} has 2 files')


if __name__ == '__main__':
    unittest.main()
