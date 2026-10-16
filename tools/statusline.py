"""Claude Code's status line for the Botropolis-City tree: where this session
is and what its tree needs, and the roadmap and the city at a glance.

Claude Code runs it on every update with the session's JSON on stdin, so it
reads only local state, never fetches, and gives up on anything slow."""

import collections
import concurrent.futures
import datetime
import json
import os
import re
import subprocess
import sys

import roadmap

META = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CHILDREN = ('botropolis', 'botropolis.city', 'vision')
GITHUB = 'https://github.com/Botropolis-City/'
REPOSITORY = {'meta': 'meta', 'botropolis': 'botropolis', 'botropolis.city': 'botropolis.city', 'vision': 'vision'}

ITEM_NAME = re.compile(r'^item (\d+)\b')
ITEM_TREE = re.compile(r'^item-(\d+)$')
BOARD = re.compile(r'https://claude\.ai/artifact/[A-Za-z0-9_-]+')

Where = collections.namedtuple('Where', 'repo root worktree')
Git = collections.namedtuple('Git', 'branch changed ahead behind unsigned')
Summary = collections.namedtuple('Summary', 'open ready blocked aria parked claims')
Facts = collections.namedtuple('Facts', 'where session item item_name item_claim git summary live city sharing '
                                        'revision release context five_hour seven_day decided board')


def where(cwd, meta=META):
    """The repository a directory is in, its root, and the worktree, if it is one."""
    rel = os.path.relpath(os.path.realpath(cwd), os.path.realpath(meta))
    if rel == os.pardir or rel.startswith(os.pardir + os.sep):
        return Where(None, None, None)
    parts = [] if rel == os.curdir else rel.split(os.sep)
    base = parts[:1] if parts[:1] and parts[0] in CHILDREN else []
    repo = base[0] if base else 'meta'
    rest = parts[len(base):]
    if rest[:2] == ['.claude', 'worktrees'] and len(rest) >= 3:
        return Where(repo, os.path.join(meta, *(base + rest[:3])), rest[2])
    return Where(repo, os.path.join(meta, *base), None)


def session_item(name, worktree):
    m = ITEM_NAME.match(name or '') or ITEM_TREE.match(worktree or '')
    return int(m.group(1)) if m else None


def summarise(items, rows):
    by = collections.defaultdict(list)
    claims = []
    for n, it in sorted(items.items()):
        if not it.is_open:
            continue
        by[roadmap.standing(it, items, rows.get(n))].append(n)
        if it.claim:
            claims.append((n, it.claim[1], it.claim[0]))
    return Summary(sum(len(v) for v in by.values()), by['ready'], by['blocked'], by['aria'], by['parked'], claims)


def age(date, today):
    try:
        days = (today - datetime.date.fromisoformat(date)).days
    except ValueError:
        return ''
    return 'today' if days <= 0 else '1 day' if days == 1 else '%d days' % days


def stale(claims, live):
    """Claimed items whose session is not alive; nothing, when that is unknown."""
    if live is None:
        return []
    return [n for n, session, _ in claims if session not in live]


def describe_git(g, worktree):
    parts = [g.branch if worktree or g.branch == 'main' else '⚠ on %s, not main' % g.branch]
    if g.changed:
        parts.append('%d changed' % g.changed)
    if g.ahead:
        parts.append('↑%d %s' % (g.ahead, 'to land' if worktree else 'unpushed'))
    if g.behind:
        parts.append('↓%d %s' % (g.behind, 'to rebase' if worktree else 'to pull'))
    if g.unsigned:
        parts.append('⚠ %d unsigned' % g.unsigned)
    if not (g.changed or g.ahead or g.behind):
        parts.append('✓')
    return parts


class Paint:
    def __init__(self, on):
        self.on = on

    def __call__(self, code, s):
        return '\033[%sm%s\033[0m' % (code, s) if self.on and s else s

    def link(self, url, s):
        return '\033]8;;%s\033\\%s\033]8;;\033\\' % (url, s) if self.on and url else s


def render(f, paint, today):
    bar = paint('2', ' │ ')
    first = []
    if f.item is not None:
        if f.item_claim and f.item_claim[1] == f.session:
            a = age(f.item_claim[0], today)
            claimed = 'claimed ' + (a if a == 'today' else a + ' ago')
        elif f.item_claim:
            claimed = paint('33', '⚠ claimed by "%s"' % f.item_claim[1])
        else:
            claimed = paint('33', '⚠ not claimed')
        head = paint('36;1', '▶ item %d' % f.item) + (' · ' + f.item_name if f.item_name else '')
        first.append(head + ' · ' + claimed)
    elif f.session:
        first.append(paint('2', f.session[:40]))
    if f.where.repo:
        name = f.where.repo + (' (private)' if f.where.repo == 'vision' else '')
        seg = paint('1', paint.link(GITHUB + REPOSITORY[f.where.repo], name))
        if f.git:
            parts = describe_git(f.git, f.where.worktree)
            seg += ' ' + ' · '.join(paint('33', p) if p.startswith('⚠') else paint('32', p) if p == '✓' else p
                                    for p in parts)
        if f.decided:
            seg += ' · %d decided' % f.decided
        if f.board:
            seg += ' · ' + paint.link(f.board, 'board')
        first.append(seg)
    claude = []
    if f.context is not None:
        claude.append(paint('31' if f.context >= 85 else '33' if f.context >= 70 else '0', 'ctx %d%%' % f.context))
    if f.five_hour is not None:
        claude.append(paint('31' if f.five_hour >= 90 else '33' if f.five_hour >= 70 else '0', '5h %d%%' % f.five_hour))
    if f.seven_day is not None and f.seven_day >= 50:
        claude.append(paint('33', '7d %d%%' % f.seven_day))
    if claude:
        first.append(' · '.join(claude))

    s = f.summary
    road = ['roadmap %d open: %d ready' % (s.open, len(s.ready))]
    if s.claims:
        road.append(paint('36', '▶ ' + ' '.join(str(n) for n, _, _ in s.claims)))
    if s.blocked:
        road.append('%d blocked' % len(s.blocked))
    if s.aria:
        road.append("%d Aria's" % len(s.aria))
    second = [' · '.join(road)]
    for n in stale(s.claims, f.live):
        second.append(paint('33', '⚠ %d: its session is gone' % n))
    if f.revision is not None:
        second.append('r%d' % f.revision + (' · ' + f.release if f.release else ''))
    if f.city:
        city = []
        if f.city.get('needs-you'):
            city.append(paint('33;1', '%d needs you' % f.city['needs-you']))
        if f.city.get('working'):
            city.append('%d working' % f.city['working'])
        if city:
            second.append('city ' + ' · '.join(city))
    if f.sharing > 1:
        second.append(paint('31;1', '⚠ %d sessions share this tree' % f.sharing))
    return [bar.join(first), bar.join(second)]


def run(args, cwd=None, timeout=1.0):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def git(root, *args):
    return run(['git', '--no-optional-locks', '-C', root] + list(args))


def git_facts(ex, root):
    branch = ex.submit(git, root, 'rev-parse', '--abbrev-ref', 'HEAD')
    status = ex.submit(git, root, 'status', '--porcelain')
    ahead = ex.submit(git, root, 'log', '--no-show-signature', '--max-count=20', '--format=%G?', 'github/main..HEAD')
    behind = ex.submit(git, root, 'rev-list', '--count', 'HEAD..github/main')

    def facts():
        b = branch.result()
        if b is None:
            return None
        signs = (ahead.result() or '').split()
        return Git(b.strip(), len((status.result() or '').splitlines()), len(signs),
                   int((behind.result() or '0').strip() or 0), sum(1 for x in signs if x in ('N', 'B')))
    return facts


def city_facts():
    out = run(['botropolis', 'status', '--json'], timeout=0.6)
    try:
        sessions = json.loads(out) if out else None
    except ValueError:
        sessions = None
    return sessions if isinstance(sessions, list) else None


def release_facts(meta):
    app = os.path.join(meta, 'botropolis')
    if not os.path.isdir(os.path.join(app, '.git')):
        return None, None
    revision = run(['git', '-C', app, 'rev-list', '--count', 'HEAD'])
    tag = (run(['git', '-C', app, 'describe', '--tags', '--abbrev=0']) or '').strip()
    try:
        version = open(os.path.join(app, 'VERSION'), encoding='utf-8').read().strip()
    except OSError:
        version = ''
    if version and tag != 'v' + version:
        release = 'v%s not tagged here' % version
    elif tag:
        since = int((run(['git', '-C', app, 'rev-list', '--count', tag + '..HEAD']) or '0').strip() or 0)
        release = tag + (' +%d' % since if since else '')
    else:
        release = None
    return (int(revision) if revision and revision.strip().isdigit() else None), release


def vision_facts(meta):
    try:
        text = open(os.path.join(meta, 'vision', 'README.md'), encoding='utf-8').read()
    except OSError:
        return None, None
    section = text.split('## Decided so far', 1)[-1].split('\n## ', 1)[0] if '## Decided so far' in text else ''
    board = BOARD.search(text)
    return sum(1 for line in section.split('\n') if line.startswith('- **')) or None, board.group(0) if board else None


def number(d, *path):
    for key in path:
        d = d.get(key) if isinstance(d, dict) else None
    return d if isinstance(d, (int, float)) else None


def gather(data, meta=META):
    workspace = data.get('workspace') or {}
    cwd = workspace.get('current_dir') or data.get('cwd') or os.getcwd()
    w = where(cwd, meta)
    session = data.get('session_name')
    n = session_item(session, w.worktree or (data.get('worktree') or {}).get('name'))
    items = roadmap.load(meta)
    try:
        rows = roadmap.open_table(open(os.path.join(meta, 'ROADMAP.md'), encoding='utf-8').read())
    except OSError:
        rows = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        git_result = git_facts(ex, w.root) if w.root else (lambda: None)
        city = ex.submit(city_facts)
        rel = ex.submit(release_facts, meta)
        g, sessions, (revision, release) = git_result(), city.result(), rel.result()
    live, counts, sharing = None, None, 0
    if sessions is not None:
        alive = [s for s in sessions if isinstance(s, dict) and s.get('alive')]
        live = {s.get('title') for s in alive}
        counts = collections.Counter(s.get('state') for s in alive)
        sharing = sum(1 for s in alive if w.root and s.get('cwd') and where(s['cwd'], meta).root == w.root)
    it = items.get(n) if n is not None else None
    decided, board = vision_facts(meta) if w.repo == 'vision' else (None, None)
    return Facts(w, session, n, it.name if it else None, it.claim if it else None, g, summarise(items, rows),
                 live, counts, sharing, revision, release, number(data, 'context_window', 'used_percentage'),
                 number(data, 'rate_limits', 'five_hour', 'used_percentage'),
                 number(data, 'rate_limits', 'seven_day', 'used_percentage'), decided, board)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    try:
        lines = render(gather(data if isinstance(data, dict) else {}), Paint(not os.environ.get('NO_COLOR')),
                       datetime.date.today())
    except Exception as e:  # a status line never shows a traceback
        lines = ['statusline: %s' % e]
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
