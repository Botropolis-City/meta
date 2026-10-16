import collections, glob, os, re, subprocess, sys

# Adapted from botropolis's tools/check_docs.py when the roadmap moved here at
# botropolis r410. Every lesson in that script still holds, and two are new:
# links reach into child repositories that may not be checked out, and this
# repository is public, so every image in it has to have been looked at.

fail = []
notes = []

def note(check, msg):
    fail.append('%s: %s' % (check, msg))

CHILDREN = ('botropolis', 'botropolis.city', 'vision')
present = {c: os.path.isdir(os.path.join(c, '.git')) for c in CHILDREN}

docs = ['ROADMAP.md', 'CLAUDE.md', 'README.md']
docs += sorted(glob.glob('roadmap/*.md'))
if present['vision']:
    docs += sorted(glob.glob('vision/*.md'))
    docs += sorted(glob.glob('vision/items/*.md'))

def targets(p):
    base = os.path.dirname(p) or '.'
    for m in re.finditer(r'\]\(([^)]+)\)', open(p, encoding='utf-8').read()):
        t = m.group(1).split('#')[0]
        if not t or t.startswith(('http', 'mailto')):
            continue
        yield os.path.normpath(os.path.join(base, t))

def child_of(path):
    top = path.split(os.sep)[0]
    return top if top in CHILDREN else None

# 1. links resolve from the linking file's own directory. A link into a child
# repository resolves only when that child is checked out here; when it is
# not, the link is skipped and the summary says so -- a skipped check that
# reads like a passing one is the fallback that hid a fault in botropolis.
links = 0
skipped = collections.Counter()
for p in docs:
    for tgt in targets(p):
        child = child_of(tgt)
        if child and not present[child]:
            skipped[child] += 1
            continue
        links += 1
        if not os.path.exists(tgt):
            note('links', '%s -> %s' % (p, tgt))

# 2. no stale section citations to the pre-split ROADMAP
NOTED = 'roadmap/inventory-2026-09-29.md'
for p in docs:
    if p in (NOTED, 'ROADMAP.md'):
        continue
    for i, line in enumerate(open(p, encoding='utf-8'), 1):
        for m in re.finditer(r'§\d+', line):
            note('citations', '%s:%d %s refers to a section that no longer exists'
                 % (p, i, m.group(0)))

# 3. every item file declares a status
items = sorted(glob.glob('roadmap/[0-9][0-9][0-9]-*.md'))
status = {}
for p in items:
    L = open(p, encoding='utf-8').read().split('\n')
    if len(L) < 3 or not L[2].startswith('**'):
        note('status', '%s has no status line under its title' % p)
        continue
    status[p] = L[2].strip('*')

# 4. ROADMAP's open table matches the item files
declared = {p for p, s in status.items() if s.lower().startswith('open')}
roadmap = open('ROADMAP.md', encoding='utf-8').read()
listed = {os.path.normpath(m)
          for m in re.findall(r'\]\((roadmap/[0-9][0-9][0-9]-[^)]+)\)', roadmap)}
for p in sorted(declared - listed):
    note('open-table', '%s is Open but ROADMAP.md does not list it' % p)
for p in sorted(listed - declared):
    note('open-table', '%s is listed in ROADMAP.md but its status is not Open (%s)'
         % (p, status.get(p, '?')[:60]))

# 5. the corpus is not empty, and no item file has gone missing. The ceiling
# comes from git, which a working-tree deletion cannot move; when git cannot
# answer, the working tree is used and the summary says so.
for index in ('ROADMAP.md', 'CLAUDE.md', 'README.md'):
    if not open(index, encoding='utf-8').read().strip():
        note('corpus', '%s is empty' % index)

numbers = {int(os.path.basename(p)[:3]) for p in items}
tracked = set()
bound_from_git = False
try:
    out = subprocess.run(['git', 'ls-files', 'roadmap/'], capture_output=True,
                         text=True, check=True).stdout.split()
    tracked = {int(os.path.basename(f)[:3])
               for f in out if re.match(r'^\d{3}-', os.path.basename(f))}
    bound_from_git = bool(tracked)
except Exception:
    pass  # not a checkout; the working tree is all there is, and the summary says so

if not numbers:
    note('corpus', 'no roadmap/NNN-*.md files found at all')
else:
    top = max(numbers | tracked)
    for n in range(1, top + 1):
        if n not in numbers:
            where = 'tracked in git' if n in tracked else 'expected'
            note('corpus', 'item %03d has no file (%s; highest known is %03d)' % (n, where, top))

# 6. nothing is orphaned. Item files are exempt, because the numbering check is
# their reachability guarantee; vision/README.md is exempt as the root of a
# repository of its own; everything else has to be linked from somewhere.
linked = set()
for p in docs:
    linked.update(targets(p))
candidates = sorted(glob.glob('roadmap/*.md'))
if present['vision']:
    candidates += sorted(glob.glob('vision/*.md'))
for p in candidates:
    if re.match(r'\d{3}-', os.path.basename(p)) or p == 'vision/README.md':
        continue
    if os.path.normpath(p) not in linked:
        note('orphans', '%s is linked from nowhere' % p)

# 7. this repository is public, so every image in it has been looked at.
# The check enumerates what exists and demands each be accounted for; a list
# of what someone remembers to check is the shape that let botropolis publish
# a GIF nobody had reviewed.
IMAGE = re.compile(r'\.(png|gif|jpe?g|webp|svg|bmp|tiff?)$', re.I)
reviewed = set()
for line in open('tools/reviewed-images.txt', encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#'):
        reviewed.add(line)
images = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d != '.git' and os.path.normpath(os.path.join(root, d)) not in CHILDREN]
    for f in files:
        if IMAGE.search(f):
            images.append(os.path.normpath(os.path.join(root, f)))
for img in sorted(images):
    if img not in reviewed:
        note('images', '%s is not on tools/reviewed-images.txt -- look at it, then add it' % img)

# 8. vision items. A vision item is an ordinary item file here -- a public
# name, a status line, what it depends on -- whose details live in the private
# vision repository, at the path its Details line names. When vision is
# checked out, every stub must point at a details file carrying its own
# number, and every details file must have a stub pointing at it. When vision
# is not, the pairing cannot be checked, and the summary says so rather than
# reading as a pass.
STUB = re.compile(r'^Details: `(vision/items/(\d{3})-[^`/]+\.md)`', re.M)
stubs = {}
for p in items:
    m = STUB.search(open(p, encoding='utf-8').read())
    if m:
        stubs[p] = (os.path.normpath(m.group(1)), m.group(2))
if present['vision']:
    details = {os.path.normpath(f) for f in glob.glob('vision/items/[0-9][0-9][0-9]-*.md')}
    pointed = set()
    for p, (path, num) in sorted(stubs.items()):
        if num != os.path.basename(p)[:3]:
            note('vision-items', '%s points at %s, which carries another number' % (p, path))
        if path not in details:
            note('vision-items', '%s points at %s, which does not exist' % (p, path))
        pointed.add(path)
    for f in sorted(details - pointed):
        note('vision-items', '%s has no stub in roadmap/ pointing at it' % f)

if fail:
    for f in fail:
        print('  %s' % f)
    print('\n%d problem(s).' % len(fail))
    sys.exit(1)
print('  %d links resolve, %d items carry a status (1-%d, none missing), open table matches, nothing orphaned, %d images reviewed.'
      % (links, len(status), max(numbers | tracked), len(images)))
if not bound_from_git:
    print('  NOTE: git did not list the roadmap, so the range came from the working tree '
          'alone. A deletion of the highest-numbered items cannot be seen from here.')
for child in CHILDREN:
    if skipped[child]:
        print('  NOTE: %d link(s) into %s/ NOT checked: %s/ is not checked out here.'
              % (skipped[child], child, child))
if not present['vision']:
    print('  NOTE: vision/ is not checked out here, so its documents were not checked.')
if stubs:
    if present['vision']:
        print('  %d vision item(s) paired with their private details.' % len(stubs))
    else:
        print('  NOTE: %d vision item(s) NOT paired with their details: vision/ is not checked out here.' % len(stubs))
