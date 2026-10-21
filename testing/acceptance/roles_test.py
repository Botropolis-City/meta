import os
import re
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from tree import ROOT, check_docs, copy_tree, remove_tree  # noqa: E402

ROLES_MD = os.path.join('docs', 'roles.md')
ROW = re.compile(r'^\| `([a-z][a-z-]*)` \| ([^|]+?) \|', re.M)


def roles(tree=ROOT):
    """The roles docs/roles.md lists, as (role, session name) pairs."""
    return ROW.findall(open(os.path.join(tree, ROLES_MD), encoding='utf-8').read())


def agent_file(tree, role):
    return os.path.join(tree, '.claude', 'agents', role + '.md')


def rewrite(path, change):
    text = open(path, encoding='utf-8').read()
    open(path, 'w', encoding='utf-8').write(change(text))


def make_dry_run(target, *assignments):
    return subprocess.run(['make', '-n', *assignments, target],
                          capture_output=True, text=True, cwd=ROOT).stdout


class WhenTheRolesAreListed(unittest.TestCase):
    def test_it_should_list_at_least_one_role(self):
        self.assertTrue(roles())


def started_role(role, name):
    class WhenTheRoleIsStarted(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.plain = make_dry_run(role)
            cls.remote = make_dry_run(role, 'REMOTE=1')

        def test_it_should_start_claude_with_its_agent(self):
            self.assertRegex(self.plain, r'claude --agent %s(\s|$)' % re.escape(role))

        def test_it_should_name_the_session(self):
            self.assertIn('-n "%s"' % name, self.plain)

        def test_it_should_not_connect_remote_control_unless_asked(self):
            self.assertNotIn('--remote-control', self.plain)

        def test_and_remote_is_set_it_should_add_remote_control(self):
            self.assertIn('--remote-control', self.remote)

    WhenTheRoleIsStarted.__name__ = 'WhenThe_%s_RoleIsStarted' % role.replace('-', '_')
    return WhenTheRoleIsStarted


for _role, _name in roles():
    _case = started_role(_role, _name)
    globals()[_case.__name__] = _case


def first_role(tree):
    return roles(tree)[0][0]


def add_stray_agent(tree):
    open(agent_file(tree, 'stray'), 'w', encoding='utf-8').write(
        '---\nname: stray\ndescription: Listed nowhere.\n---\n')


def delete_first_agent(tree):
    os.remove(agent_file(tree, first_role(tree)))


def rename_first_agent(tree):
    rewrite(agent_file(tree, first_role(tree)),
            lambda t: re.sub(r'^name: .*$', 'name: somebody-else', t, count=1, flags=re.M))


def drop_first_description(tree):
    rewrite(agent_file(tree, first_role(tree)),
            lambda t: re.sub(r'^description:.*?(?=^[a-z]+:|^---)', '', t, count=1, flags=re.M | re.S))


def pin_first_model(tree):
    rewrite(agent_file(tree, first_role(tree)), lambda t: t.replace('---\n', '---\nmodel: opus\n', 1))


def give_first_project_memory(tree):
    rewrite(agent_file(tree, first_role(tree)), lambda t: t.replace('---\n', '---\nmemory: project\n', 1))


def give_first_an_unknown_skill(tree):
    rewrite(agent_file(tree, first_role(tree)),
            lambda t: re.sub(r'^skills: \[', 'skills: [no-such-skill, ', t, count=1, flags=re.M))


def with_vision_checked_out(mutate):
    def both(tree):
        os.makedirs(os.path.join(tree, 'vision', '.git'))
        os.makedirs(os.path.join(tree, 'vision', '.claude', 'skills'))
        mutate(tree)
    return both


def empty_the_role_table(tree):
    rewrite(os.path.join(tree, ROLES_MD), lambda t: ROW.sub('', t))


MUTATIONS = [
    ('AnAgentFileIsNotListed', add_stray_agent,
     r'roles: \.claude/agents/stray\.md is not listed in docs/roles\.md'),
    ('ARoleHasNoAgentFile', delete_first_agent,
     r'roles: [a-z-]+ is listed in docs/roles\.md and has no \.claude/agents/[a-z-]+\.md'),
    ('AnAgentIsNamedForAnotherRole', rename_first_agent,
     r'roles: \.claude/agents/[a-z-]+\.md is named somebody-else'),
    ('AnAgentHasNoDescription', drop_first_description,
     r'roles: \.claude/agents/[a-z-]+\.md has no description'),
    ('AnAgentPinsAModel', pin_first_model,
     r'roles: \.claude/agents/[a-z-]+\.md pins a model'),
    ('AnAgentUsesProjectMemory', give_first_project_memory,
     r'roles: \.claude/agents/[a-z-]+\.md uses project memory'),
    ('AnAgentNamesASkillThatDoesNotExist', with_vision_checked_out(give_first_an_unknown_skill),
     r'roles: \.claude/agents/[a-z-]+\.md names the skill no-such-skill, which does not exist'),
    ('TheRoleTableIsEmpty', empty_the_role_table,
     r'roles: docs/roles\.md lists no roles'),
]


def mutated(name, mutate, expected):
    class WhenMutated(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.tree = copy_tree()
            mutate(cls.tree)
            cls.result = check_docs(cls.tree)

        @classmethod
        def tearDownClass(cls):
            remove_tree(cls.tree)

        def test_it_should_fail(self):
            self.assertNotEqual(self.result.returncode, 0)

        def test_it_should_name_what_is_wrong(self):
            self.assertRegex(self.result.stdout, expected)

    WhenMutated.__name__ = 'When' + name
    return WhenMutated


for _name, _mutate, _expected in MUTATIONS:
    _case = mutated(_name, _mutate, _expected)
    globals()[_case.__name__] = _case


class WhenAnAgentNamesAnUnknownSkillAndVisionIsNotCheckedOut(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = copy_tree()
        give_first_an_unknown_skill(cls.tree)
        cls.result = check_docs(cls.tree)

    @classmethod
    def tearDownClass(cls):
        remove_tree(cls.tree)

    def test_it_should_say_the_skill_went_unchecked(self):
        self.assertRegex(self.result.stdout, r'NOTE: .*no-such-skill.* NOT checked: vision/ is not checked out here')


if __name__ == '__main__':
    unittest.main()
