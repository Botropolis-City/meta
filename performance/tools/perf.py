import datetime
import json
import os
import re
import sys
import time
import uuid

UNITS_KIB = {'B': 1 / 1024, 'KiB': 1, 'kB': 1, 'MiB': 1024, 'GiB': 1024 * 1024}

SAMPLE_FIELDS = [
    'ts', 'elapsed_s', 'pid', 'comm', 'cpu_pct',
    'rss_kib', 'pss_kib', 'pss_anon_kib', 'pss_file_kib', 'private_dirty_kib', 'swap_kib',
    'gpu_kib', 'threads', 'fds', 'read_kib_s', 'write_kib_s', 'mem_available_kib',
]

SUMMARY_METRICS = [
    ('cpu_pct', 'cpu_pct', 1),
    ('private_dirty_kib', 'private_dirty_mib', 1024),
    ('pss_kib', 'pss_mib', 1024),
    ('swap_kib', 'swap_mib', 1024),
    ('gpu_kib', 'gpu_mib', 1024),
    ('threads', 'threads', 1),
    ('fds', 'fds', 1),
    ('read_kib_s', 'read_mib_s', 1024),
    ('write_kib_s', 'write_mib_s', 1024),
]

GCTRACE = re.compile(r'^gc \d+ @(?P<at>[\d.]+)s .* (?P<start>\d+)->(?P<end>\d+)->(?P<live>\d+) MB, (?P<goal>\d+) MB goal')


def parse_smaps_rollup(text):
    out = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0].endswith(':') and parts[2] == 'kB':
            out[parts[0][:-1]] = int(parts[1])
    return out


def drm_total_kib(fdinfos):
    clients = {}
    for text in fdinfos:
        fields = {}
        for line in text.splitlines():
            key, _, value = line.partition(':')
            fields[key.strip()] = value.strip()
        if 'drm-client-id' not in fields:
            continue
        total = 0
        for key, value in fields.items():
            if key.startswith('drm-total-'):
                amount, _, unit = value.partition(' ')
                total += int(amount) * UNITS_KIB.get(unit or 'B', 1)
        clients[(fields.get('drm-driver'), fields['drm-client-id'])] = total
    if not clients:
        return None
    return int(sum(clients.values()))


def cpu_percent(before_ticks, after_ticks, clk_tck, interval_s):
    if interval_s <= 0:
        return 0.0
    return (after_ticks - before_ticks) * 100.0 / clk_tck / interval_s


def parse_proc_io(text):
    out = {}
    for line in text.splitlines():
        key, _, value = line.partition(':')
        if value.strip().isdigit():
            out[key.strip()] = int(value)
    return out


def rate_kib_s(before, after, interval_s):
    if before is None or after is None or interval_s <= 0:
        return None
    return (after - before) / 1024 / interval_s


def proc_io(pid):
    return parse_proc_io(read('/proc/%d/io' % pid) or '')


def slope_per_minute(xs, ys):
    if len(xs) < 2:
        return None
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den * 60


def percentile(values, p):
    ordered = sorted(values)
    if not ordered:
        return None
    index = max(0, min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1))))
    return ordered[index]


def parse_gctrace_line(line):
    m = GCTRACE.search(line.strip())
    if not m:
        return None
    return {
        'at_s': float(m['at']),
        'start_mb': int(m['start']),
        'end_mb': int(m['end']),
        'live_mb': int(m['live']),
        'goal_mb': int(m['goal']),
    }


def summarise(rows, by_pid=False):
    by_comm = {}
    for row in rows:
        key = '%s[%s]' % (row['comm'], row['pid']) if by_pid else row['comm']
        by_comm.setdefault(key, []).append(row)
    out = {}
    for comm, group in by_comm.items():
        stats = {'samples': len(group), 'pids': sorted({r['pid'] for r in group})}
        xs = [float(r['elapsed_s']) for r in group]
        for field, name, divisor in SUMMARY_METRICS:
            pairs = [(x, float(r[field]) / divisor) for x, r in zip(xs, group) if r.get(field) not in (None, '')]
            if not pairs:
                continue
            values = [v for _, v in pairs]
            stats[name] = {
                'first': values[0],
                'last': values[-1],
                'min': min(values),
                'max': max(values),
                'mean': sum(values) / len(values),
                'p50': percentile(values, 50),
                'p95': percentile(values, 95),
                'slope_per_min': slope_per_minute([x for x, _ in pairs], values),
            }
        out[comm] = stats
    return out


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return None


def proc_ticks(pid):
    text = read('/proc/%d/stat' % pid)
    if text is None:
        return None
    fields = text[text.rindex(')') + 2:].split()
    return int(fields[11]) + int(fields[12])


def proc_comm(pid):
    text = read('/proc/%d/comm' % pid)
    return text.strip() if text else None


def proc_children(pid):
    found = set()
    for tid in os.listdir('/proc/%d/task' % pid) if os.path.isdir('/proc/%d/task' % pid) else []:
        text = read('/proc/%d/task/%s/children' % (pid, tid)) or ''
        found.update(int(c) for c in text.split())
    return found


def proc_tree(pid):
    seen = set()
    stack = [pid]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        stack.extend(proc_children(p))
    return seen


def pids_named(names):
    out = set()
    for entry in os.listdir('/proc'):
        if entry.isdigit() and proc_comm(int(entry)) in names:
            out.add(int(entry))
    return out


def proc_snapshot(pid):
    rollup = parse_smaps_rollup(read('/proc/%d/smaps_rollup' % pid) or '')
    status = read('/proc/%d/status' % pid) or ''
    threads = re.search(r'^Threads:\s+(\d+)', status, re.M)
    fd_dir = '/proc/%d/fd' % pid
    try:
        fds = os.listdir(fd_dir)
    except OSError:
        fds = []
    fdinfos = []
    for fd in fds:
        try:
            if os.readlink(os.path.join(fd_dir, fd)).startswith('/dev/dri/'):
                fdinfos.append(read('/proc/%d/fdinfo/%s' % (pid, fd)) or '')
        except OSError:
            pass
    return {
        'rss_kib': rollup.get('Rss'),
        'pss_kib': rollup.get('Pss'),
        'pss_anon_kib': rollup.get('Pss_Anon'),
        'pss_file_kib': rollup.get('Pss_File'),
        'private_dirty_kib': rollup.get('Private_Dirty'),
        'swap_kib': rollup.get('Swap'),
        'gpu_kib': drm_total_kib(fdinfos),
        'threads': int(threads[1]) if threads else None,
        'fds': len(fds),
    }


def mem_available_kib():
    m = re.search(r'^MemAvailable:\s+(\d+)', read('/proc/meminfo') or '', re.M)
    return int(m[1]) if m else None


class IdleClock:
    def __init__(self, threshold_pct, needed_s):
        self.threshold_pct = threshold_pct
        self.needed_s = needed_s
        self.quiet_since = None
        self.last = None

    def observe(self, at_s, cpu_pct):
        self.last = at_s
        if cpu_pct >= self.threshold_pct:
            self.quiet_since = None
        elif self.quiet_since is None:
            self.quiet_since = at_s

    def idle(self):
        return self.quiet_since is not None and self.last - self.quiet_since >= self.needed_s


def i3_window_ids(tree):
    ids = []
    stack = [tree]
    while stack:
        node = stack.pop()
        if node.get('window'):
            ids.append(node['window'])
        stack.extend(node.get('nodes', []) + node.get('floating_nodes', []))
    return ids


def busy_home(real_claude, home):
    claude = os.path.join(home, '.claude')
    projects = os.path.join(real_claude, 'projects')
    for project in sorted(os.listdir(projects)) if os.path.isdir(projects) else []:
        src = os.path.join(projects, project)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(claude, 'projects', project)
        os.makedirs(dst, exist_ok=True)
        for name in sorted(os.listdir(src)):
            path = os.path.join(src, name)
            if name.endswith('.jsonl') or os.path.isdir(path):
                link = os.path.join(dst, name)
                if not os.path.lexists(link):
                    os.symlink(path, link)
    sessions = os.path.join(real_claude, 'sessions')
    os.makedirs(os.path.join(claude, 'sessions'), exist_ok=True)
    for name in sorted(os.listdir(sessions)) if os.path.isdir(sessions) else []:
        link = os.path.join(claude, 'sessions', name)
        if name.endswith('.json') and not os.path.lexists(link):
            os.symlink(os.path.join(sessions, name), link)
    history = os.path.join(real_claude, 'history.jsonl')
    if os.path.exists(history):
        link = os.path.join(claude, 'history.jsonl')
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(history, link)


def replay_targets(home):
    claude = os.path.join(home, '.claude')
    targets = []
    sessions = os.path.join(claude, 'sessions')
    for name in sorted(os.listdir(sessions)) if os.path.isdir(sessions) else []:
        record = os.path.join(sessions, name)
        if os.path.islink(record) or not name.endswith('.json'):
            continue
        with open(record) as f:
            r = json.load(f)
        sid, cwd = r.get('sessionId'), r.get('cwd')
        projects = os.path.join(claude, 'projects')
        for project in sorted(os.listdir(projects)) if os.path.isdir(projects) else []:
            path = os.path.join(projects, project, '%s.jsonl' % sid)
            if os.path.isfile(path) and not os.path.islink(path):
                targets.append((sid, cwd, path))
                break
    return targets


def replay_line(session_id, cwd, i, timestamp):
    return {'type': 'user', 'sessionId': session_id, 'cwd': cwd, 'uuid': str(uuid.uuid4()),
            'timestamp': timestamp, 'message': {'role': 'user', 'content': 'replay %d' % i}}


def append_line(path, line):
    if os.path.islink(path):
        raise PermissionError('refusing to write through a symlink: %s' % path)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
    with os.fdopen(fd, 'a') as f:
        f.write(json.dumps(line) + '\n')


def replay(home, writers, seconds, every=0.2):
    targets = replay_targets(home)[:writers]
    if len(targets) < writers:
        sys.exit('only %d live transcripts of the scratch home itself to write to' % len(targets))
    print('replaying into %d transcripts' % len(targets), flush=True)
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
        for sid, cwd, path in targets:
            append_line(path, replay_line(sid, cwd, i, now))
        i += 1
        time.sleep(every)
    print('appended %d lines to each' % i, flush=True)


USAGE = """usage: perf.py i3-window-ids < tree.json
       perf.py busy-home REAL_CLAUDE_DIR HOME   link every transcript, session record and history.jsonl into HOME/.claude, read only
       perf.py replay HOME WRITERS SECONDS      a user line every 200 ms into each of WRITERS of HOME's own live transcripts"""

if __name__ == '__main__':
    cmd = sys.argv[1:2]
    if cmd == ['i3-window-ids']:
        print('\n'.join(str(w) for w in i3_window_ids(json.load(sys.stdin))))
    elif cmd == ['busy-home'] and len(sys.argv) == 4:
        busy_home(sys.argv[2], sys.argv[3])
    elif cmd == ['replay'] and len(sys.argv) == 5:
        replay(sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    else:
        sys.exit(USAGE)
