"""The roadmap's grammar, shared by tools/check_docs.py, which enforces it, and
tools/statusline, which reads it, so that the two cannot disagree about what a
status line, a claim, a dependency or a landed slice looks like."""

import collections
import glob
import os
import re

ITEMS = 'roadmap/[0-9][0-9][0-9]-*.md'

CLAIM = re.compile(r'^Open, in progress since (\d{4}-\d{2}-\d{2}) in the session "([^"]+)"\. ')
DEPENDS = re.compile(r'^Depends on: ?(.*)$', re.M)
DEP = re.compile(r'^(\d+)(?: \(slice (\d+)\))?$')
LANDED_ANY = re.compile(r'^Landed:.*$', re.M)
LANDED = re.compile(r'^Landed: slice (\d+) \(`([0-9a-f]{7,40})`, r(\d+)\)\.$')
DETAILS_ANY = re.compile(r'^Details:.*$', re.M)
DETAILS = re.compile(r'^Details: `(vision/items/[^`/]+\.md)`, in the private vision repository\.$')
STUB_TITLE = re.compile(r'^# (\d+)\. [A-Z][a-z]+(?: [a-z]+)*, part (\d+)$')
STUB_LINES = ('Depends on: ', 'Landed: ', 'Details: ')
ROW = re.compile(r'^\| \[(\d+)\]\(roadmap/\d{3}-[^)]+\) \| (.*) \| (.*) \| (.*) \|$')

Row = collections.namedtuple('Row', 'what depends whose')


class Item:
    def __init__(self, path, text):
        self.path = os.path.normpath(path)
        self.number = int(os.path.basename(path)[:3])
        self.lines = text.split('\n')
        heading = self.lines[0]
        self.name = heading.split('. ', 1)[1].strip() if heading.startswith('# ') and '. ' in heading else ''
        third = self.lines[2] if len(self.lines) > 2 else ''
        self.status = third.strip().strip('*') if third.startswith('**') else None
        self.is_open = (self.status or '').lower().startswith('open')
        m = CLAIM.match(self.status or '')
        self.claim = (m.group(1), m.group(2)) if m else None
        d = DEPENDS.search(text)
        self.depends_raw = d.group(1).strip() if d else None
        self.landed_lines = LANDED_ANY.findall(text)
        self.landed = {int(m.group(1)) for m in map(LANDED.match, self.landed_lines) if m}
        self.details_lines = DETAILS_ANY.findall(text)
        self.vision = bool(self.details_lines)
        m = DETAILS.match(self.details_lines[0]) if self.details_lines else None
        self.details = os.path.normpath(m.group(1)) if m else None

    @property
    def deps(self):
        try:
            return parse_depends(self.depends_raw)
        except ValueError:
            return []


def parse_depends(raw):
    """'nothing' or '82 (slice 1), 85' -> [(82, 1), (85, None)]."""
    if raw is None or raw == 'nothing':
        return []
    out = []
    for part in raw.split(', '):
        m = DEP.match(part)
        if not m:
            raise ValueError(part)
        out.append((int(m.group(1)), int(m.group(2)) if m.group(2) else None))
    return out


def load(root='.'):
    items = {}
    for p in sorted(glob.glob(os.path.join(root, ITEMS))):
        with open(p, encoding='utf-8') as f:
            it = Item(os.path.relpath(p, root), f.read())
        items[it.number] = it
    return items


def open_table(text):
    rows = {}
    for line in text.split('\n'):
        m = ROW.match(line.strip())
        if m:
            rows[int(m.group(1))] = Row(*(c.strip() for c in m.group(2, 3, 4)))
    return rows


def standing(item, items, row):
    """Where an open item stands: in progress, aria, parked, blocked or ready."""
    if item.claim:
        return 'in progress'
    whose = (row.whose if row else '').lower()
    if whose.startswith('aria'):
        return 'aria'
    if 'until' in whose:
        return 'parked'
    for n, s in item.deps:
        dep = items.get(n)
        if dep is not None and dep.is_open and (s is None or s not in dep.landed):
            return 'blocked'
    return 'ready'
