import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from tree import ROOT, check_docs, copy_tree, remove_tree  # noqa: E402


class WhenTheDocumentationIsChecked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = check_docs(ROOT)

    def test_it_should_find_nothing_wrong(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)


class WhenTwoItemsShareANumber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = copy_tree()
        first = sorted(p for p in os.listdir(os.path.join(cls.tree, 'roadmap'))
                       if p[:3].isdigit())[0]
        shutil.copy2(os.path.join(cls.tree, 'roadmap', first),
                     os.path.join(cls.tree, 'roadmap', first[:4] + 'a-second-file-with-the-same-number.md'))
        cls.result = check_docs(cls.tree)

    @classmethod
    def tearDownClass(cls):
        remove_tree(cls.tree)

    def test_it_should_name_the_number_used_twice(self):
        self.assertRegex(self.result.stdout, r'item \d{3} has 2 files')


if __name__ == '__main__':
    unittest.main()
