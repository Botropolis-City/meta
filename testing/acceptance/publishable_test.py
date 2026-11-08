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


TOKEN = 'zorblax'


def write(cwd, name, text):
    with open(os.path.join(cwd, name), 'w') as f:
        f.write(text)


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

    def merge_pull_request(self, number, commits):
        """Push `commits` (name, text, message) to refs/pull/N/head, then squash-merge their final tree into main."""
        git(self.other, 'pull', '-q', '--rebase', 'github', 'main')
        git(self.other, 'checkout', '-q', '-b', f'pull-{number}')
        for name, text, message in commits:
            write(self.other, name, text)
            git(self.other, 'add', name)
            git(self.other, 'commit', '-q', '-m', message)
        git(self.other, 'push', '-q', 'github', f'HEAD:refs/pull/{number}/head')
        git(self.other, 'checkout', '-q', 'main')
        git(self.other, 'merge', '-q', '--squash', f'pull-{number}')
        git(self.other, 'commit', '-q', '-m', f'Squashed pull request {number}')
        git(self.other, 'push', '-q', 'github', 'HEAD:main')

    def list_tokens(self):
        write(self.worktree, '.publishable-tokens', TOKEN + '\n')

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


class WhenAMergedPullRequestsRefIsOutsideTheHistoryBeingPublished:
    class Case(unittest.TestCase):
        commits = ()
        tokens = True

        @classmethod
        def setUpClass(cls):
            cls.repos = Repositories()
            cls.repos.merge_pull_request(1, cls.commits)
            cls.repos.rebase_worktree()
            if cls.tokens:
                cls.repos.list_tokens()
            cls.result = check(cls.repos.worktree)

        @classmethod
        def tearDownClass(cls):
            cls.repos.remove()

    class AndItsCommitsAreClean(Case):
        commits = (('feature', 'a feature\n', 'Add a feature'),
                   ('feature', 'a better feature\n', 'Improve the feature'))

        def test_it_should_pass(self):
            self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)

        def test_it_should_name_the_pull_requests_ref(self):
            self.assertIn('refs/pull/1/head', self.result.stdout)

    class AndAFileItAddsCarriesAToken(Case):
        commits = (('feature', f'made for {TOKEN}\n', 'Add a feature'),
                   ('feature', 'made for nobody\n', 'Take the name out'))

        def test_it_should_fail(self):
            self.assertEqual(self.result.returncode, 1, self.result.stdout + self.result.stderr)

        def test_it_should_name_the_pull_requests_ref(self):
            self.assertIn('refs/pull/1/head', self.result.stdout)

    class AndItsCommitMessageCarriesAToken(Case):
        commits = (('feature', 'a feature\n', f'Add the feature {TOKEN} asked for'),)

        def test_it_should_fail(self):
            self.assertEqual(self.result.returncode, 1, self.result.stdout + self.result.stderr)

        def test_it_should_name_the_pull_requests_ref(self):
            self.assertIn('refs/pull/1/head', self.result.stdout)

    class AndThereIsNoTokensList(Case):
        commits = (('feature', 'a feature\n', 'Add a feature'),)
        tokens = False

        def test_it_should_pass(self):
            self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)

        def test_it_should_say_the_pull_requests_ref_was_not_swept(self):
            self.assertRegex(self.result.stdout, r'refs/pull/1/head[^.]*NOT swept')


class WhenARemoteBranchIsOutsideTheHistoryBeingPublished(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repos = Repositories()
        git(cls.repos.other, 'checkout', '-q', '-b', 'side')
        commit(cls.repos.other, 'never landed')
        git(cls.repos.other, 'push', '-q', 'github', 'side')
        cls.repos.list_tokens()
        cls.result = check(cls.repos.worktree)

    @classmethod
    def tearDownClass(cls):
        cls.repos.remove()

    def test_it_should_fail(self):
        self.assertEqual(self.result.returncode, 1, self.result.stdout + self.result.stderr)

    def test_it_should_name_the_branch(self):
        self.assertIn('refs/heads/side', self.result.stdout)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for case in (WhenPublishableRunsInTheMainClone,
                 WhenPublishableRunsInAWorktree.AndTheLocalMainIsBehindTheRemote,
                 WhenPublishableRunsInAWorktree.AndARemoteTagIsOutsideTheHistoryBeingPublished,
                 WhenPublishableRunsInAWorktree.AndTheRemoteMainIsAheadOfHead,
                 WhenAMergedPullRequestsRefIsOutsideTheHistoryBeingPublished.AndItsCommitsAreClean,
                 WhenAMergedPullRequestsRefIsOutsideTheHistoryBeingPublished.AndAFileItAddsCarriesAToken,
                 WhenAMergedPullRequestsRefIsOutsideTheHistoryBeingPublished.AndItsCommitMessageCarriesAToken,
                 WhenAMergedPullRequestsRefIsOutsideTheHistoryBeingPublished.AndThereIsNoTokensList,
                 WhenARemoteBranchIsOutsideTheHistoryBeingPublished):
        suite.addTests(loader.loadTestsFromTestCase(case))
    return suite


if __name__ == '__main__':
    unittest.main()
