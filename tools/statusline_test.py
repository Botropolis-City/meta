import datetime
import unittest

import roadmap
import statusline

META = '/w/botropolis-city'


def item(number, status, *body, name='A title'):
    text = '\n'.join(['# %d. %s' % (number, name), '', '**%s**' % status, ''] + list(body)) + '\n'
    return roadmap.Item('roadmap/%03d-a-title.md' % number, text)


class WhenLocatingTheSession(unittest.TestCase):
    def test_it_should_name_the_repository_and_worktree_a_directory_is_in(self):
        for cwd, want in [
            (META, ('meta', META, None)),
            (META + '/roadmap', ('meta', META, None)),
            (META + '/botropolis', ('botropolis', META + '/botropolis', None)),
            (META + '/botropolis/pkg/plan', ('botropolis', META + '/botropolis', None)),
            (META + '/botropolis.city/site', ('botropolis.city', META + '/botropolis.city', None)),
            (META + '/vision/items', ('vision', META + '/vision', None)),
            (META + '/botropolis/.claude/worktrees/item-85/pkg',
             ('botropolis', META + '/botropolis/.claude/worktrees/item-85', 'item-85')),
            (META + '/.claude/worktrees/item-9', ('meta', META + '/.claude/worktrees/item-9', 'item-9')),
            ('/elsewhere/project', (None, None, None)),
        ]:
            with self.subTest(cwd=cwd):
                self.assertEqual(tuple(statusline.where(cwd, META)), want)


class WhenFindingTheSessionsItem(unittest.TestCase):
    def test_it_should_read_the_number_from_the_name_or_the_worktree(self):
        for name, worktree, want in [
            ('item 85', None, 85),
            ('item 85 launch test', None, 85),
            (None, 'item-85', 85),
            ('planning', 'item-87', 87),
            ('botropolis design research', None, None),
            ('an item 85 lookalike', None, None),
            (None, None, None),
        ]:
            with self.subTest(name=name, worktree=worktree):
                self.assertEqual(statusline.session_item(name, worktree), want)


class WhenSummarisingTheRoadmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        items = [
            item(69, 'Open. Filed.'),
            item(70, 'Open. Filed.'),
            item(66, 'Open. Filed.'),
            item(82, 'Open, in progress since 2026-10-15 in the session "item 82". Filed.'),
            item(83, 'Open. Filed.', 'Depends on: 82 (slice 1)'),
            item(81, 'Done 2026-10-14 (`abc1234`, r405). Filed.'),
        ]
        rows = {
            69: roadmap.Row('a bar', '—', 'Aria'),
            70: roadmap.Row('a fix', '—', 'nobody, a known fix'),
            66: roadmap.Row('a curiosity', '—', 'nobody, until it costs something'),
            82: roadmap.Row('the finder', '—', 'nobody'),
            83: roadmap.Row('a pane', '82 (slice 1)', 'nobody'),
        }
        cls.summary = statusline.summarise({i.number: i for i in items}, rows)

    def test_it_should_count_the_open_items(self):
        self.assertEqual(self.summary.open, 5)

    def test_it_should_list_what_is_ready(self):
        self.assertEqual(self.summary.ready, [70])

    def test_it_should_list_what_is_blocked(self):
        self.assertEqual(self.summary.blocked, [83])

    def test_it_should_list_what_waits_on_aria(self):
        self.assertEqual(self.summary.aria, [69])

    def test_it_should_list_what_is_parked(self):
        self.assertEqual(self.summary.parked, [66])

    def test_it_should_list_each_claim_with_its_session_and_date(self):
        self.assertEqual(self.summary.claims, [(82, 'item 82', '2026-10-15')])


class WhenAgeingAClaim(unittest.TestCase):
    def test_it_should_say_how_long_ago_it_was_made(self):
        today = datetime.date(2026, 10, 15)
        for date, want in [('2026-10-15', 'today'), ('2026-10-14', '1 day'), ('2026-10-01', '14 days'), ('nonsense', '')]:
            with self.subTest(date=date):
                self.assertEqual(statusline.age(date, today), want)


class WhenCheckingClaimsAgainstLiveSessions(unittest.TestCase):
    claims = [(82, 'item 82', '2026-10-15'), (86, 'item 86', '2026-10-15')]

    def test_and_a_claims_session_is_alive_it_should_not_be_stale(self):
        self.assertEqual(statusline.stale(self.claims, {'item 82', 'item 86'}), [])

    def test_and_a_claims_session_is_gone_it_should_be_stale(self):
        self.assertEqual(statusline.stale(self.claims, {'item 82'}), [86])

    def test_and_the_live_sessions_are_unknown_it_should_judge_nothing(self):
        self.assertEqual(statusline.stale(self.claims, None), [])


class WhenDescribingGit(unittest.TestCase):
    def test_it_should_say_what_the_tree_and_branch_need(self):
        for info, worktree, want in [
            (statusline.Git('main', 0, 0, 0, 0), None, ['main', '✓']),
            (statusline.Git('main', 3, 0, 0, 0), None, ['main', '3 changed']),
            (statusline.Git('main', 0, 2, 0, 0), None, ['main', '↑2 unpushed']),
            (statusline.Git('main', 0, 0, 4, 0), None, ['main', '↓4 to pull']),
            (statusline.Git('worktree-item-85', 0, 1, 0, 0), 'item-85', ['worktree-item-85', '↑1 to land']),
            (statusline.Git('worktree-item-85', 0, 0, 2, 0), 'item-85', ['worktree-item-85', '↓2 to rebase']),
            (statusline.Git('main', 0, 2, 0, 1), None, ['main', '↑2 unpushed', '⚠ 1 unsigned']),
            (statusline.Git('feature', 0, 0, 0, 0), None, ['⚠ on feature, not main', '✓']),
        ]:
            with self.subTest(info=info, worktree=worktree):
                self.assertEqual(statusline.describe_git(info, worktree), want)


class WhenReadingMainsCIRecord(unittest.TestCase):
    def test_it_should_read_the_state_the_commit_and_when_it_was_checked(self):
        checked = datetime.datetime(2026, 10, 22, 11, 0, tzinfo=datetime.timezone.utc)
        for text, want in [
            ('red abc1234 2026-10-22T11:00:00Z\n', statusline.CI('red', 'abc1234', checked)),
            ('green abc1234 2026-10-22T11:00:00Z', statusline.CI('green', 'abc1234', checked)),
            ('unknown - 2026-10-22T11:00:00Z', statusline.CI('unknown', None, checked)),
            ('', None),
            ('purple abc1234 2026-10-22T11:00:00Z', None),
            ('red abc1234 yesterday', None),
        ]:
            with self.subTest(text=text):
                self.assertEqual(statusline.parse_ci(text), want)


class WhenDescribingMainsCI(unittest.TestCase):
    def test_it_should_say_what_a_landing_last_saw_of_it(self):
        now = datetime.datetime(2026, 10, 22, 12, 0, tzinfo=datetime.timezone.utc)
        fresh, old = now - datetime.timedelta(hours=1), now - datetime.timedelta(days=2, hours=1)
        for ci, want in [
            (None, 'ci unchecked'),
            (statusline.CI('green', 'abc1234', fresh), None),
            (statusline.CI('green', 'abc1234', old), 'ci green 2d ago'),
            (statusline.CI('red', 'abc1234', fresh), 'ci red abc1234'),
            (statusline.CI('red', 'abc1234', old), 'ci red abc1234, 2d ago'),
            (statusline.CI('unknown', None, fresh), 'ci ?'),
            (statusline.CI('unknown', None, old), 'ci ?, 2d ago'),
        ]:
            with self.subTest(ci=ci):
                self.assertEqual(statusline.describe_ci(ci, now), want)


class WhenRenderingWithoutColour(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        summary = statusline.Summary(open=5, ready=[70], blocked=[83], aria=[69], parked=[66],
                                     claims=[(82, 'item 82', '2026-10-15')])
        facts = statusline.Facts(
            where=statusline.Where('botropolis', META + '/botropolis/.claude/worktrees/item-82', 'item-82'),
            session='item 82', item=82, item_name='Find a session', item_claim=('2026-10-15', 'item 82'),
            git=statusline.Git('worktree-item-82', 2, 1, 0, 0), summary=summary, live={'item 82'},
            city={'needs-you': 1, 'working': 2}, sharing=1, revision=412, release='v0.1.7 +3',
            context=34, five_hour=23.5, seven_day=None, decided=None, board=None, ci='ci red abc1234')
        cls.lines = statusline.render(facts, statusline.Paint(False), datetime.date(2026, 10, 15))

    def test_it_should_print_two_lines(self):
        self.assertEqual(len(self.lines), 2)

    def test_it_should_lead_with_the_item_being_worked(self):
        self.assertTrue(self.lines[0].startswith('▶ item 82 · Find a session · claimed today'))

    def test_it_should_show_what_the_worktree_needs(self):
        self.assertIn('2 changed · ↑1 to land', self.lines[0])

    def test_it_should_show_the_roadmap_at_a_glance(self):
        self.assertTrue(self.lines[1].startswith('roadmap 5 open: 1 ready · ▶ 82 · 1 blocked · 1 Aria\'s'))

    def test_it_should_show_the_city(self):
        self.assertIn('1 needs you · 2 working', self.lines[1])

    def test_it_should_show_mains_ci(self):
        self.assertIn('r412 · v0.1.7 +3 · ci red abc1234', self.lines[1])

    def test_it_should_contain_no_escape_codes(self):
        self.assertNotIn('\033', ''.join(self.lines))


if __name__ == '__main__':
    unittest.main()
