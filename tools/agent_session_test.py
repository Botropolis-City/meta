import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest

import agent_session

CWD = '/w/botropolis-city'
TITLE = 'roadmap manager'


class WhenNamingTheProjectDirectory(unittest.TestCase):
    def test_it_should_replace_every_non_alphanumeric_with_a_dash(self):
        for cwd, want in [
            ('/home/a/workspaces/github/botropolis-city', '-home-a-workspaces-github-botropolis-city'),
            ('/home/a/botropolis/.claude/worktrees/item-350', '-home-a-botropolis--claude-worktrees-item-350'),
            ('/w/x_y.z', '-w-x-y-z'),
        ]:
            with self.subTest(cwd=cwd):
                self.assertEqual(agent_session.project_dir(cwd, '/p'), '/p/' + want)


class WhenChoosingTheSessionToResume(unittest.TestCase):
    def setUp(self):
        self.projects = tempfile.mkdtemp(prefix='agent-session-')
        self.addCleanup(shutil.rmtree, self.projects)
        self.project = agent_session.project_dir(CWD, self.projects)
        os.makedirs(self.project)

    def session(self, sid, *lines, age=0):
        path = os.path.join(self.project, sid + '.jsonl')
        with open(path, 'w') as f:
            for line in lines:
                f.write(json.dumps(line) + '\n')
        now = 1_800_000_000
        os.utime(path, (now - age, now - age))
        return sid

    @staticmethod
    def titled(sid, title=TITLE):
        return {'type': 'custom-title', 'customTitle': title, 'sessionId': sid}

    @staticmethod
    def user(text='hello'):
        return {'type': 'user', 'message': {'role': 'user', 'content': text}}

    def latest(self):
        return agent_session.latest(TITLE, CWD, self.projects)

    def test_it_should_pick_the_newest_session_carrying_the_title(self):
        self.session('old', self.titled('old'), self.user(), age=100)
        self.session('new', self.titled('new'), self.user(), age=10)
        self.session('older', self.titled('older'), self.user(), age=1000)
        self.assertEqual(self.latest(), 'new')

    def test_it_should_skip_a_session_that_never_received_a_message(self):
        self.session('spoken', self.titled('spoken'), self.user(), age=100)
        self.session('empty', self.titled('empty'), age=10)
        self.assertEqual(self.latest(), 'spoken')

    def test_it_should_skip_a_title_that_names_another_session(self):
        self.session('mine', self.titled('mine'), self.user(), age=100)
        self.session('borrowed', self.titled('mine'), self.user(), age=10)
        self.assertEqual(self.latest(), 'mine')

    def test_it_should_skip_a_session_whose_title_was_changed(self):
        self.session('kept', self.titled('kept'), self.user(), age=100)
        self.session('renamed', self.titled('renamed'), self.user(), self.titled('renamed', 'something else'), age=10)
        self.assertEqual(self.latest(), 'kept')

    def test_it_should_ignore_the_title_inside_a_message_body(self):
        self.session('mentions', self.user('ask the "roadmap manager"'), age=10)
        self.assertIsNone(self.latest())

    def test_it_should_return_none_when_nothing_carries_the_title(self):
        self.session('other', self.titled('other', 'design agent'), self.user())
        self.assertIsNone(self.latest())

    def test_it_should_return_none_when_the_project_has_no_directory(self):
        self.assertIsNone(agent_session.latest(TITLE, '/nowhere', self.projects))


class WhenRunAsACommand(WhenChoosingTheSessionToResume):
    def run_main(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = agent_session.main(['--cwd', CWD, '--projects', self.projects, TITLE])
        return code, out.getvalue(), err.getvalue()

    def test_it_should_print_the_session_id(self):
        self.session('found', self.titled('found'), self.user())
        self.assertEqual(self.run_main()[:2], (0, 'found\n'))

    def test_it_should_fail_and_say_so_when_there_is_nothing_to_resume(self):
        code, out, err = self.run_main()
        self.assertEqual((code, out, TITLE in err and self.project in err), (1, '', True))


if __name__ == '__main__':
    unittest.main()
