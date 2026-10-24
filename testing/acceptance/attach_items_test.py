import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOL = os.path.join(ROOT, 'tools', 'attach-items')

CLAUDE = '''#!/usr/bin/env bash
if [[ "$1" == agents ]]; then cat "$ATTACH_TEST_AGENTS"; exit 0; fi
exec sleep 600
'''


@unittest.skipUnless(shutil.which('tmux') and shutil.which('jq'), 'needs tmux and jq')
class AttachItems(unittest.TestCase):
    agents = []
    windows = {}

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        bin_dir = os.path.join(cls.tmp, 'bin')
        os.mkdir(bin_dir)
        claude = os.path.join(bin_dir, 'claude')
        with open(claude, 'w') as f:
            f.write(CLAUDE)
        os.chmod(claude, 0o755)
        agents = os.path.join(cls.tmp, 'agents.json')
        with open(agents, 'w') as f:
            json.dump([{'id': i, 'name': n} for n, i in cls.agents], f)
        cls.env = {k: v for k, v in os.environ.items() if k != 'TMUX'}
        cls.env.update(PATH=bin_dir + os.pathsep + os.environ['PATH'],
                       TMUX_TMPDIR=cls.tmp, ATTACH_TEST_AGENTS=agents)
        for name, command in cls.windows.items():
            cls.tmux('new-session' if name == next(iter(cls.windows)) else 'new-window',
                     *(['-d', '-s', 'items'] if name == next(iter(cls.windows)) else ['-d', '-t', '=items:']),
                     '-n', name, command)
        cls.before = cls.panes()
        cls.run_ = subprocess.run([TOOL], env=cls.env, capture_output=True, text=True)
        cls.after = cls.panes()

    @classmethod
    def tearDownClass(cls):
        subprocess.run(['tmux', 'kill-server'], env=cls.env, capture_output=True)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def tmux(cls, *args):
        return subprocess.run(['tmux', *args], env=cls.env, capture_output=True, text=True, check=True).stdout

    @classmethod
    def panes(cls):
        try:
            out = cls.tmux('list-panes', '-s', '-t', '=items', '-F', '#W\t#{pane_pid}\t#{pane_start_command}')
        except subprocess.CalledProcessError:
            return {}
        rows = (line.split('\t', 2) for line in out.splitlines())
        return {w: (pid, cmd.strip('"')) for w, pid, cmd in rows}


class WhenNoWindowExistsForALiveItem(AttachItems):
    agents = [('item 7', 'aaaa1111')]

    def test_it_should_open_one_attached_to_its_session(self):
        self.assertEqual('claude attach aaaa1111', self.after['item-007'][1])


class WhenTheItemsWindowIsAttachedToItsSession(AttachItems):
    agents = [('item 7', 'aaaa1111')]
    windows = {'item-007': 'claude attach aaaa1111'}

    def test_it_should_leave_the_window_alone(self):
        self.assertEqual(self.before['item-007'][0], self.after['item-007'][0])


class WhenTheItemsWindowRunsSomethingElse(AttachItems):
    agents = [('item 7', 'aaaa1111')]
    windows = {'item-007': 'sleep 600'}

    def test_it_should_attach_the_window_to_the_items_session(self):
        self.assertEqual('claude attach aaaa1111', self.after['item-007'][1])


class WhenTheItemsWindowIsAttachedToAnotherSession(AttachItems):
    agents = [('item 7', 'aaaa1111')]
    windows = {'item-007': 'claude attach bbbb2222'}

    def test_it_should_attach_the_window_to_the_items_current_session(self):
        self.assertEqual('claude attach aaaa1111', self.after['item-007'][1])


class WhenAWindowsItemHasNoSession(AttachItems):
    agents = [('item 7', 'aaaa1111')]
    windows = {'item-007': 'claude attach aaaa1111', 'item-009': 'claude attach cccc3333'}

    def test_it_should_close_the_window(self):
        self.assertNotIn('item-009', self.after)


if __name__ == '__main__':
    unittest.main()
