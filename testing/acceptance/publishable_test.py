import os
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'check-publishable')

ENV = dict(
    os.environ,
    GIT_CONFIG_GLOBAL=os.devnull,
    GIT_CONFIG_NOSYSTEM='1',
    GIT_AUTHOR_NAME='Test',
    GIT_AUTHOR_EMAIL='test@example.com',
    GIT_COMMITTER_NAME='Test',
    GIT_COMMITTER_EMAIL='test@example.com',
)


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, env=ENV, check=True,
                          capture_output=True, text=True).stdout.strip()


def commit(cwd, name):
    with open(os.path.join(cwd, name), 'w') as f:
        f.write(name + '\n')
    git(cwd, 'add', name)
    git(cwd, 'commit', '-q', '-m', name)


def check(cwd):
    return subprocess.run([os.path.join(cwd, 'tools', 'check-publishable')], cwd=cwd, env=ENV,
                          capture_output=True, text=True)


class Repositories:
    """A bare `github` remote, the main clone, a second clone that lands, and a worktree of the main clone."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix='publishable-')
        self.remote = os.path.join(self.root, 'remote.git')
        self.clone = os.path.join(self.root, 'clone')
        self.other = os.path.join(self.root, 'other')
        self.worktree = os.path.join(self.root, 'worktree')
        git(self.root, 'init', '-q', '--bare', '-b', 'main', self.remote)
        git(self.root, 'clone', '-q', '-o', 'github', self.remote, self.clone)
        git(self.clone, 'checkout', '-q', '-b', 'main')
        os.makedirs(os.path.join(self.clone, 'tools'))
        shutil.copy2(SCRIPT, os.path.join(self.clone, 'tools', 'check-publishable'))
        git(self.clone, 'add', 'tools')
        git(self.clone, 'commit', '-q', '-m', 'the guard')
        git(self.clone, 'push', '-q', 'github', 'main')
        git(self.root, 'clone', '-q', '-o', 'github', self.remote, self.other)
        git(self.clone, 'worktree', 'add', '-q', '-b', 'item', self.worktree, 'main')

    def land_from_other(self, name):
        git(self.other, 'pull', '-q', '--rebase', 'github', 'main')
        commit(self.other, name)
        git(self.other, 'push', '-q', 'github', 'HEAD:main')

    def rebase_worktree(self):
        git(self.worktree, 'fetch', '-q', 'github')
        git(self.worktree, 'rebase', '-q', 'github/main')

    def remove(self):
        shutil.rmtree(self.root, ignore_errors=True)


class WhenPublishableRunsInTheMainClone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repos = Repositories()
        cls.repos.land_from_other('landed elsewhere')
        git(cls.repos.clone, 'pull', '-q', '--rebase', 'github', 'main')
        cls.result = check(cls.repos.clone)

    @classmethod
    def tearDownClass(cls):
        cls.repos.remove()

    def test_and_it_is_up_to_date_it_should_pass(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)


class WhenPublishableRunsInAWorktree(unittest.TestCase):
    class AndTheLocalMainIsBehindTheRemote(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.repos = Repositories()
            cls.repos.land_from_other('landed elsewhere')
            cls.repos.rebase_worktree()
            commit(cls.repos.worktree, 'this item')
            cls.result = check(cls.repos.worktree)

        @classmethod
        def tearDownClass(cls):
            cls.repos.remove()

        def test_it_should_pass(self):
            self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)

    class AndARemoteTagIsOutsideTheHistoryBeingPublished(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.repos = Repositories()
            git(cls.repos.other, 'checkout', '-q', '-b', 'side')
            commit(cls.repos.other, 'never landed')
            git(cls.repos.other, 'tag', 'stray')
            git(cls.repos.other, 'push', '-q', 'github', 'refs/tags/stray')
            git(cls.repos.worktree, 'fetch', '-q', '--tags', 'github')
            cls.result = check(cls.repos.worktree)

        @classmethod
        def tearDownClass(cls):
            cls.repos.remove()

        def test_it_should_fail(self):
            self.assertEqual(self.result.returncode, 1, self.result.stdout + self.result.stderr)

        def test_it_should_name_the_tag(self):
            self.assertIn('refs/tags/stray', self.result.stdout)

    class AndTheRemoteMainIsAheadOfHead(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.repos = Repositories()
            cls.repos.rebase_worktree()
            cls.repos.land_from_other('landed after the rebase')
            git(cls.repos.worktree, 'fetch', '-q', 'github')
            cls.result = check(cls.repos.worktree)

        @classmethod
        def tearDownClass(cls):
            cls.repos.remove()

        def test_it_should_fail(self):
            self.assertEqual(self.result.returncode, 1, self.result.stdout + self.result.stderr)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for case in (WhenPublishableRunsInTheMainClone,
                 WhenPublishableRunsInAWorktree.AndTheLocalMainIsBehindTheRemote,
                 WhenPublishableRunsInAWorktree.AndARemoteTagIsOutsideTheHistoryBeingPublished,
                 WhenPublishableRunsInAWorktree.AndTheRemoteMainIsAheadOfHead):
        suite.addTests(loader.loadTestsFromTestCase(case))
    return suite


if __name__ == '__main__':
    unittest.main()
