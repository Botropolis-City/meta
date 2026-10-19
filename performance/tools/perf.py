import os
import re

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
