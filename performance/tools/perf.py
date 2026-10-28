import csv
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
    'gpu_kib', 'gpu_shared_kib', 'gpu_resident_kib', 'gpu_purgeable_kib', 'gpu_active_kib', 'gpu_regions',
    'threads', 'fds', 'read_kib_s', 'write_kib_s', 'mem_available_kib',
]

SUMMARY_METRICS = [
    ('cpu_pct', 'cpu_pct', 1),
    ('private_dirty_kib', 'private_dirty_mib', 1024),
    ('pss_kib', 'pss_mib', 1024),
    ('swap_kib', 'swap_mib', 1024),
    ('gpu_kib', 'gpu_mib', 1024),
    ('gpu_shared_kib', 'gpu_shared_mib', 1024),
    ('gpu_resident_kib', 'gpu_resident_mib', 1024),
    ('gpu_purgeable_kib', 'gpu_purgeable_mib', 1024),
    ('gpu_active_kib', 'gpu_active_mib', 1024),
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


DRM_KINDS = ('total', 'shared', 'resident', 'purgeable', 'active')


def drm_clients(fdinfos):
    clients = {}
    for text in fdinfos:
        fields = {}
        for line in text.splitlines():
            key, _, value = line.partition(':')
            fields[key.strip()] = value.strip()
        if 'drm-client-id' not in fields:
            continue
        regions = {}
        for key, value in fields.items():
            for kind in DRM_KINDS:
                prefix = 'drm-%s-' % kind
                if key.startswith(prefix):
                    amount, _, unit = value.partition(' ')
                    region = regions.setdefault(key[len(prefix):], dict.fromkeys(DRM_KINDS, 0))
                    region[kind] += int(amount) * UNITS_KIB.get(unit or 'B', 1)
        clients[(fields.get('drm-driver'), fields['drm-client-id'])] = regions
    return clients


def drm_kib(fdinfos, kind):
    clients = drm_clients(fdinfos)
    if not clients:
        return None
    return int(sum(r[kind] for regions in clients.values() for r in regions.values()))


def drm_total_kib(fdinfos):
    return drm_kib(fdinfos, 'total')


def drm_regions(fdinfos):
    by_region = {}
    for regions in drm_clients(fdinfos).values():
        for name, amounts in regions.items():
            into = by_region.setdefault(name, dict.fromkeys(DRM_KINDS, 0))
            for kind in DRM_KINDS:
                into[kind] += amounts[kind]
    return ' '.join('%s=%s' % (name, '/'.join(str(int(by_region[name][k])) for k in DRM_KINDS))
                    for name in sorted(by_region))


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


def sample_epoch(row):
    return datetime.datetime.fromisoformat(row['ts']).timestamp()


def phase_samples(rows, start, end, comm='botropolis'):
    """The city's own memory and GPU together, in MiB, at each sample in [start, end)."""
    by_ts = {}
    for row in rows:
        if row['comm'] != comm or not start <= sample_epoch(row) < end:
            continue
        kib = sum(float(row[f]) for f in ('private_dirty_kib', 'gpu_kib') if row.get(f) not in (None, ''))
        by_ts[row['ts']] = by_ts.get(row['ts'], 0) + kib / 1024
    return [by_ts[ts] for ts in sorted(by_ts)]


def phase_summary(rows, start, end, comm='botropolis'):
    values = phase_samples(rows, start, end, comm)
    if not values:
        return None
    return {'least': min(values), 'most': max(values), 'mean': sum(values) / len(values), 'samples': len(values)}


def print_phases(samples_path, marks_path):
    """The settled phases of a perf-fitzoom run: fit 30-90 s and full zoom 150-215 s."""
    with open(samples_path) as f:
        rows = list(csv.DictReader(f))
    marks = {}
    with open(marks_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and parts[0] not in ('window',):
                marks[parts[0]] = int(parts[1])
    start = marks['fit']
    print('| phase | seconds | samples | own + GPU MiB, least | most | mean |')
    print('| --- | --- | --- | --- | --- | --- |')
    for name, a, b in (('settled at fit', 30, 90), ('settled at full zoom', 150, 215)):
        s = phase_summary(rows, start + a, start + b)
        if s is None:
            print('| %s | %d-%d | 0 | - | - | - |' % (name, a, b))
        else:
            print('| %s | %d-%d | %d | %.0f | %.0f | %.0f |' % (name, a, b, s['samples'], s['least'], s['most'], s['mean']))


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
        'gpu_shared_kib': drm_kib(fdinfos, 'shared'),
        'gpu_resident_kib': drm_kib(fdinfos, 'resident'),
        'gpu_purgeable_kib': drm_kib(fdinfos, 'purgeable'),
        'gpu_active_kib': drm_kib(fdinfos, 'active'),
        'gpu_regions': drm_regions(fdinfos),
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


def xwininfo_size(text):
    w = re.search(r'^\s*Width:\s*(\d+)', text, re.M)
    h = re.search(r'^\s*Height:\s*(\d+)', text, re.M)
    return '%sx%s' % (w[1], h[1]) if w and h else None


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


def check_inside(home, path):
    claude = os.path.realpath(os.path.join(home, '.claude'))
    if os.path.islink(path) or os.path.commonpath([claude, os.path.realpath(path)]) != claude:
        raise PermissionError('refusing to write outside the scratch home: %s' % path)


def is_inside(home, path):
    try:
        check_inside(home, path)
    except PermissionError:
        return False
    return True


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
            if os.path.isfile(path) and is_inside(home, path):
                targets.append((sid, cwd, path, r.get('status')))
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
        for sid, cwd, path, _ in targets:
            append_line(path, replay_line(sid, cwd, i, now))
        i += 1
        time.sleep(every)
    print('appended %d lines to each' % i, flush=True)


LOOK_CYCLE_S = 30
LOOK_ATTENTION_S = 10
LOOK_TOOL_EVERY_S = 3
LOOK_COMPACT_EVERY_S = 60
LOOK_OFFSET_S = 7


def look_events(c):
    q = c % LOOK_CYCLE_S
    events = []
    if c % LOOK_COMPACT_EVERY_S == 0:
        events.append('compact')
    if q == 0:
        events.append('attention-in')
    elif q == LOOK_ATTENTION_S:
        events.append('attention-out')
    starts = range(LOOK_ATTENTION_S + 1, LOOK_CYCLE_S - LOOK_TOOL_EVERY_S, LOOK_TOOL_EVERY_S)
    if q in starts:
        events.append('tool-start')
    elif q - 1 in starts:
        events.append('tool-end')
    return events


def _line(kind, session_id, cwd, timestamp, **fields):
    line = {'type': kind, 'sessionId': session_id, 'cwd': cwd, 'uuid': str(uuid.uuid4()),
            'timestamp': timestamp, 'isSidechain': False}
    line.update(fields)
    return line


def _tool_use(session_id, cwd, timestamp, name, tool_id, tool_input):
    return _line('assistant', session_id, cwd, timestamp, message={
        'id': 'msg_replay_%s' % uuid.uuid4().hex, 'role': 'assistant', 'stop_reason': 'tool_use',
        'content': [{'type': 'tool_use', 'id': tool_id, 'name': name, 'input': tool_input}]})


def _tool_result(session_id, cwd, timestamp, tool_id):
    return _line('user', session_id, cwd, timestamp, message={
        'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': tool_id, 'content': 'replayed'}]})


def look_lines(event, session_id, cwd, status, timestamp, ids):
    new_id = 'toolu_replay_%s' % uuid.uuid4().hex
    if event == 'tool-start':
        ids['tool'] = new_id
        return [_tool_use(session_id, cwd, timestamp, 'Bash', new_id, {'command': 'true'})]
    if event == 'tool-end':
        return [_tool_result(session_id, cwd, timestamp, ids.pop('tool'))] if 'tool' in ids else []
    if event == 'compact':
        return [_line('system', session_id, cwd, timestamp, subtype='compact_boundary', content='Conversation compacted',
                      compactMetadata={'trigger': 'auto', 'preTokens': 150000})]
    if event == 'attention-in' and status == 'idle':
        return [_tool_use(session_id, cwd, timestamp, 'ScheduleWakeup', new_id, {'delaySeconds': 60}),
                _tool_result(session_id, cwd, timestamp, new_id)]
    if event == 'attention-in':
        ids['ask'] = new_id
        return [_tool_use(session_id, cwd, timestamp, 'AskUserQuestion', new_id, {'questions': []})]
    if event == 'attention-out' and status == 'idle':
        return [_line('user', session_id, cwd, timestamp, message={'role': 'user', 'content': 'replay: carry on'})]
    if event == 'attention-out':
        return [_tool_result(session_id, cwd, timestamp, ids.pop('ask'))] if 'ask' in ids else []
    raise ValueError('no look event %r' % event)


def replay_looks(home, writers, seconds, clock=time.time, sleep=time.sleep, out=sys.stdout):
    targets = replay_targets(home)[:writers]
    if len(targets) < writers:
        sys.exit('only %d live transcripts of the scratch home itself to write to' % len(targets))
    for _, _, path, _ in targets:
        check_inside(home, path)
    print('replaying looks into %d transcripts' % len(targets), file=out, flush=True)
    ids = [{} for _ in targets]
    written = 0
    start = clock()
    for t in range(int(seconds)):
        delay = start + t - clock()
        if delay > 0:
            sleep(delay)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
        for i, (sid, cwd, path, status) in enumerate(targets):
            for event in look_events(t + LOOK_OFFSET_S * i):
                for line in look_lines(event, sid, cwd, status, now, ids[i]):
                    check_inside(home, path)
                    append_line(path, line)
                    written += 1
    print('appended %d look lines across %d transcripts' % (written, len(targets)), file=out, flush=True)


def slope_per_hour(xs, ys):
    per_minute = slope_per_minute(xs, ys)
    return None if per_minute is None else per_minute * 60


def read_marks(text):
    marks = {}
    for line in text.splitlines():
        key, sep, value = line.partition('=')
        if sep and key and ' ' not in key:
            marks[key] = value.strip()
    return marks


SOAK_BUDGET_MIB_H = 1.0
SOAK_SETTLE_S = 600
SOAK_MIN_PHASE_S = 1800


def soak_phases(marks, end_s, settle_s=SOAK_SETTLE_S):
    hidden_at = marks.get('hidden_at_s')
    if hidden_at is None:
        return {'visible': (settle_s, end_s)}
    hidden_at = int(float(hidden_at))
    return {'visible': (settle_s, hidden_at), 'hidden': (hidden_at + settle_s, end_s)}


def soak_series(rows, process, daemon_pid):
    by_at = {}
    for row in rows:
        if process == 'city' and row['comm'] != 'botropolis':
            continue
        if process == 'daemon' and (row['comm'] != 'botropolisd' or row['pid'] != str(daemon_pid)):
            continue
        kib = sum(float(row[f]) for f in ('private_dirty_kib', 'gpu_kib') if row.get(f) not in (None, ''))
        at = float(row['elapsed_s'])
        by_at[at] = by_at.get(at, 0) + kib / 1024
    return sorted(by_at.items())


SOAK_STEP_MIB = 8.0
SOAK_STEP_NOISES = 4


def soak_parts(rows, process, daemon_pid):
    by_at = {}
    for row in rows:
        if process == 'city' and row['comm'] != 'botropolis':
            continue
        if process == 'daemon' and (row['comm'] != 'botropolisd' or row['pid'] != str(daemon_pid)):
            continue
        at = float(row['elapsed_s'])
        ts, pd, gpu = by_at.get(at, (row.get('ts', ''), 0.0, 0.0))
        pd += float(row.get('private_dirty_kib') or 0) / 1024
        gpu += float(row.get('gpu_kib') or 0) / 1024
        by_at[at] = (ts, pd, gpu)
    return [(at,) + parts for at, parts in sorted(by_at.items())]


def noise_mib(diffs):
    if not diffs:
        return 0.0
    ordered = sorted(diffs)
    mid = ordered[len(ordered) // 2]
    deviations = sorted(abs(d - mid) for d in diffs)
    return 1.4826 * deviations[len(deviations) // 2]


def utc_of(ts):
    try:
        local = datetime.datetime.fromisoformat(ts)
    except ValueError:
        return ''
    return local.astimezone(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def soak_steps(rows, phases, daemon_pid):
    steps = []
    for process in ('city', 'daemon'):
        parts = soak_parts(rows, process, daemon_pid)
        for phase, (start, end) in phases.items():
            inside = [p for p in parts if start <= p[0] <= end]
            totals = [pd + gpu for _, _, pd, gpu in inside]
            diffs = [b - a for a, b in zip(totals, totals[1:])]
            threshold = max(SOAK_STEP_MIB, SOAK_STEP_NOISES * noise_mib(diffs))
            for i, d in enumerate(diffs):
                if abs(d) <= threshold:
                    continue
                before, after = inside[:i + 1], inside[i + 1:]
                at, ts = inside[i + 1][0], inside[i + 1][1]
                steps.append({
                    'process': process, 'phase': phase, 'at_s': at, 'box': ts, 'utc': utc_of(ts),
                    'private_dirty_mib': inside[i + 1][2] - inside[i][2], 'gpu_mib': inside[i + 1][3] - inside[i][3],
                    'before_mib_h': slope_per_hour([p[0] for p in before], [p[2] + p[3] for p in before]),
                    'after_mib_h': slope_per_hour([p[0] for p in after], [p[2] + p[3] for p in after]),
                })
    return steps


def judge_soak(rows, marks, budget_mib_h=SOAK_BUDGET_MIB_H, settle_s=SOAK_SETTLE_S, min_phase_s=SOAK_MIN_PHASE_S):
    reasons = []
    end_s = max((float(r['elapsed_s']) for r in rows), default=0)
    phases = soak_phases(marks, end_s, settle_s)
    hiding = marks.get('hide') != 'none'
    if hiding and 'hidden_at_s' not in marks:
        reasons.append('the window was never hidden, so there is no hidden phase')
    if int(marks.get('frames_at_hide' if hiding else 'frames_at_end') or 0) <= 0:
        reasons.append('the visible phase drew no frames')
    if 'monitor is on' not in marks.get('monitor_at_end', '').lower():
        reasons.append('the monitor was not on at the end (%s), so the visible phase may not have drawn'
                       % (marks.get('monitor_at_end') or 'unchecked'))
    if not marks.get('daemon_pid'):
        reasons.append("the scratch daemon's pid was not recorded")
    judged = []
    for process in ('city', 'daemon'):
        series = soak_series(rows, process, marks.get('daemon_pid'))
        for phase, (start, end) in phases.items():
            inside = [(x, y) for x, y in series if start <= x <= end]
            span = inside[-1][0] - inside[0][0] if inside else 0
            if span < min_phase_s:
                reasons.append('%s %s holds %.0f s of samples, under %d s' % (process, phase, span, min_phase_s))
            slope = slope_per_hour([x for x, _ in inside], [y for _, y in inside])
            judged.append({'process': process, 'phase': phase, 'start_s': start, 'end_s': end,
                           'samples': len(inside), 'slope_mib_h': slope,
                           'over': slope is not None and slope > budget_mib_h})
    if reasons:
        verdict = 'not a measurement'
    elif any(p['over'] for p in judged):
        verdict = 'fail'
    else:
        verdict = 'pass'
    return {'verdict': verdict, 'reasons': reasons, 'phases': judged, 'budget_mib_h': budget_mib_h,
            'steps': soak_steps(rows, phases, marks.get('daemon_pid'))}


SOAK_EXIT = {'pass': 0, 'fail': 1, 'not a measurement': 2}

SOAK_NOTES = ('display', 'hide', 'hidden_at_s', 'hide_failed_at_s', 'frames_at_hide', 'frames_at_end', 'daemon_pid',
              'monitor_at_start', 'monitor_at_end', 'load_at_start', 'load_at_end', 'landings_during', 'demo_hold')


def soak_report(result, marks):
    lines = ['# Soak verdict: %s' % result['verdict'], '',
             'Budget: growth of at most %.1f MiB an hour of `Private_Dirty` + GPU, per process and phase '
             '(performance/budgets.md).' % result['budget_mib_h'], '',
             'Light: %s' % (marks.get('light') or 'live, following the clock'), '']
    for reason in result['reasons']:
        lines.append('- not a measurement: %s' % reason)
    if result['reasons']:
        lines.append('')
    lines += ['| process | phase | seconds | samples | MiB/hour | over |', '| --- | --- | --- | --- | --- | --- |']
    for p in result['phases']:
        slope = '-' if p['slope_mib_h'] is None else '%.2f' % p['slope_mib_h']
        lines.append('| %s | %s | %.0f-%.0f | %d | %s | %s |' % (p['process'], p['phase'], p['start_s'], p['end_s'],
                                                              p['samples'], slope, 'yes' if p['over'] else 'no'))
    lines.append('')
    lines += soak_step_lines(result.get('steps', []))
    lines.append('')
    lines += ['- %s: %s' % (key, marks[key]) for key in SOAK_NOTES if key in marks]
    return '\n'.join(lines) + '\n'


def soak_step_lines(steps):
    rule = ('two samples differing by more than %.0f MiB of `Private_Dirty` + GPU, or four times the phase\'s '
            'sample-to-sample noise, whichever is larger; a step still counts in its phase\'s slope' % SOAK_STEP_MIB)
    if not steps:
        return ['No steps: no %s.' % rule.split(';')[0]]
    lines = ['## Steps', '', 'A step is %s.' % rule, '',
             '| process | phase | second | box clock | UTC | Private_Dirty MiB | GPU MiB | MiB/hour before | MiB/hour after |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']

    def slope(v):
        return '-' if v is None else '%.2f' % v
    for s in steps:
        lines.append('| %s | %s | %.0f | %s | %s | %+.1f | %+.1f | %s | %s |' % (
            s['process'], s['phase'], s['at_s'], s['box'], s['utc'], s['private_dirty_mib'], s['gpu_mib'],
            slope(s['before_mib_h']), slope(s['after_mib_h'])))
    return lines


def print_soak_verdict(samples_path, *marks_paths):
    try:
        with open(samples_path) as f:
            rows = list(csv.DictReader(f))
    except OSError:
        rows = []
    marks = {}
    for path in marks_paths:
        marks.update(read_marks(read(path) or ''))
    result = judge_soak(rows, marks,
                        settle_s=int(os.environ.get('PERF_SOAK_SETTLE', SOAK_SETTLE_S)),
                        min_phase_s=int(os.environ.get('PERF_SOAK_MIN_PHASE', SOAK_MIN_PHASE_S)))
    sys.stdout.write(soak_report(result, marks))
    return SOAK_EXIT[result['verdict']]


USAGE = """usage: perf.py i3-window-ids < tree.json
       perf.py window-size < xwininfo.txt        the window's WIDTHxHEIGHT, or nothing
       perf.py busy-home REAL_CLAUDE_DIR HOME   link every transcript, session record and history.jsonl into HOME/.claude, read only
       perf.py replay HOME WRITERS SECONDS      a user line every 200 ms into each of WRITERS of HOME's own live transcripts
       perf.py replay --looks HOME WRITERS SECONDS
                                                instead, lines that change each writer's look: a tool call every 3 s,
                                                needs-you (or waiting, on an idle record) 10 s in every 30, and a
                                                compaction every 60 s, writers 7 s apart in phase (item 312)
       perf.py phase-summary SAMPLES MARKS      a perf-fitzoom run's own + GPU MiB, settled at fit and at full zoom
       perf.py soak-verdict SAMPLES MARKS...    a perf-soak run's growth per process and phase;
                                                exit 0 within budget, 1 over it, 2 not a measurement"""

if __name__ == '__main__':
    cmd = sys.argv[1:2]
    if cmd == ['i3-window-ids']:
        print('\n'.join(str(w) for w in i3_window_ids(json.load(sys.stdin))))
    elif cmd == ['phase-summary'] and len(sys.argv) == 4:
        print_phases(sys.argv[2], sys.argv[3])
    elif cmd == ['soak-verdict'] and len(sys.argv) >= 4:
        sys.exit(print_soak_verdict(sys.argv[2], *sys.argv[3:]))
    elif cmd == ['window-size']:
        print(xwininfo_size(sys.stdin.read()) or '')
    elif cmd == ['busy-home'] and len(sys.argv) == 4:
        busy_home(sys.argv[2], sys.argv[3])
    elif cmd == ['replay'] and len(sys.argv) == 6 and sys.argv[2] == '--looks':
        replay_looks(sys.argv[3], int(sys.argv[4]), float(sys.argv[5]))
    elif cmd == ['replay'] and len(sys.argv) == 5:
        replay(sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    else:
        sys.exit(USAGE)
