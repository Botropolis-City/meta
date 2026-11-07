"""Find the newest Claude Code session a role can resume.

A role's make target names its session (-n "roadmap manager"), and Claude
Code records that name in the session's transcript under
~/.claude/projects/<working directory, with every non-alphanumeric as a
dash>/<session id>.jsonl.  The newest transcript that carries the name as
its own, current title and holds at least one user message is the one to
resume: one that never received a message has nothing to come back to.
"""

import argparse
import json
import os
import re
import sys

PROJECTS = os.path.expanduser('~/.claude/projects')


def project_dir(cwd, projects=PROJECTS):
    return os.path.join(projects, re.sub(r'[^A-Za-z0-9]', '-', cwd))


def resumable(path, title):
    sid = os.path.basename(path)[:-len('.jsonl')]
    titled = False
    spoken = False
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if '"custom-title"' in line:
                entry = _entry(line)
                if entry.get('type') == 'custom-title' and entry.get('sessionId') == sid:
                    titled = entry.get('customTitle') == title
            elif not spoken and '"user"' in line:
                spoken = _entry(line).get('type') == 'user'
    return titled and spoken


def _entry(line):
    try:
        return json.loads(line)
    except ValueError:
        return {}


def latest(title, cwd, projects=PROJECTS):
    directory = project_dir(cwd, projects)
    try:
        names = os.listdir(directory)
    except OSError:
        return None
    paths = [os.path.join(directory, n) for n in names if n.endswith('.jsonl')]
    for path in sorted(paths, key=os.path.getmtime, reverse=True):
        if resumable(path, title):
            return os.path.basename(path)[:-len('.jsonl')]
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='agent-session',
        description='Print the id of the newest session named TITLE that was started from --cwd and can be resumed.')
    parser.add_argument('title')
    parser.add_argument('--cwd', default=os.getcwd(), help='the directory the session was started from (default: here)')
    parser.add_argument('--projects', default=PROJECTS, help="Claude Code's projects directory (default: %(default)s)")
    args = parser.parse_args(argv)
    sid = latest(args.title, args.cwd, args.projects)
    if sid is None:
        print('agent-session: no session named "%s" to resume under %s'
              % (args.title, project_dir(args.cwd, args.projects)), file=sys.stderr)
        return 1
    print(sid)
    return 0


if __name__ == '__main__':
    sys.exit(main())
