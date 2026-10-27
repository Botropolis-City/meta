import json
import os
import subprocess
import tempfile
import unittest

import perf

HERE = os.path.dirname(os.path.abspath(__file__))

SMAPS_ROLLUP = """309ff8000000-7ffc63834000 ---p 00000000 00:00 0                          [rollup]
Rss:               28672 kB
Pss:               26651 kB
Pss_Anon:          18140 kB
Pss_File:           8511 kB
Private_Dirty:     18160 kB
Swap:               1204 kB
"""

DRM_FDINFO = """pos:\t0
flags:\t02100002
drm-driver:\txe
drm-client-id:\t42
drm-total-system:\t1024 KiB
drm-total-vram0:\t2 MiB
drm-resident-system:\t512 KiB
"""

DRM_FDINFO_SAME_CLIENT = DRM_FDINFO

DRM_FDINFO_OTHER_CLIENT = """drm-driver:\ti915
drm-client-id:\t43
drm-total-local0:\t4096 KiB
"""

NOT_DRM_FDINFO = """pos:\t0
flags:\t02
inotify wd:1 ino:2 sdev:3 mask:4
"""


class WhenParsingSmapsRollup(unittest.TestCase):
    def setUp(self):
        self.parsed = perf.parse_smaps_rollup(SMAPS_ROLLUP)

    def test_it_should_read_private_dirty_in_kib(self):
        self.assertEqual(self.parsed['Private_Dirty'], 18160)

    def test_it_should_read_pss_in_kib(self):
        self.assertEqual(self.parsed['Pss'], 26651)

    def test_it_should_skip_the_header_line(self):
        self.assertNotIn('309ff8000000-7ffc63834000', self.parsed)


class WhenSummingDrmFdinfo(unittest.TestCase):
    def test_and_one_client_holds_memory_it_should_sum_every_region(self):
        self.assertEqual(perf.drm_total_kib([DRM_FDINFO]), 1024 + 2048)

    def test_and_two_fds_share_one_client_it_should_count_the_client_once(self):
        self.assertEqual(perf.drm_total_kib([DRM_FDINFO, DRM_FDINFO_SAME_CLIENT]), 3072)

    def test_and_two_clients_are_open_it_should_add_them(self):
        self.assertEqual(perf.drm_total_kib([DRM_FDINFO, DRM_FDINFO_OTHER_CLIENT]), 3072 + 4096)

    def test_and_no_fd_is_a_drm_client_it_should_report_none(self):
        self.assertIsNone(perf.drm_total_kib([NOT_DRM_FDINFO]))


I915_FDINFO = """drm-driver:\ti915
drm-client-id:\t7
drm-total-system0:\t3 MiB
drm-shared-system0:\t1024 KiB
drm-active-system0:\t0
drm-resident-system0:\t2048 KiB
drm-purgeable-system0:\t512 KiB
drm-total-stolen-local0:\t64 KiB
drm-shared-stolen-local0:\t0
drm-active-stolen-local0:\t16 KiB
drm-resident-stolen-local0:\t64 KiB
drm-purgeable-stolen-local0:\t0
"""

I915_FDINFO_OTHER_CLIENT = """drm-driver:\ti915
drm-client-id:\t8
drm-shared-system0:\t256 KiB
"""


class WhenReadingDrmMemoryByKind(unittest.TestCase):
    cases = [
        ('total', [I915_FDINFO], 3072 + 64),
        ('shared', [I915_FDINFO], 1024),
        ('resident', [I915_FDINFO], 2048 + 64),
        ('purgeable', [I915_FDINFO], 512),
        ('active', [I915_FDINFO], 16),
        ('shared', [I915_FDINFO, I915_FDINFO], 1024),
        ('shared', [I915_FDINFO, I915_FDINFO_OTHER_CLIENT], 1024 + 256),
    ]

    def test_it_should_sum_each_kind_over_regions_once_per_client(self):
        for kind, fdinfos, want in self.cases:
            with self.subTest(kind=kind, fds=len(fdinfos)):
                self.assertEqual(perf.drm_kib(fdinfos, kind), want)

    def test_and_no_fd_is_a_drm_client_it_should_report_none(self):
        self.assertIsNone(perf.drm_kib([NOT_DRM_FDINFO], 'resident'))


class WhenDescribingDrmRegions(unittest.TestCase):
    def test_it_should_give_each_region_its_total_shared_resident_purgeable_and_active_kib(self):
        self.assertEqual(perf.drm_regions([I915_FDINFO, I915_FDINFO_OTHER_CLIENT]),
                         'stolen-local0=64/0/64/0/16 system0=3072/1280/2048/512/0')

    def test_and_no_fd_is_a_drm_client_it_should_be_empty(self):
        self.assertEqual(perf.drm_regions([NOT_DRM_FDINFO]), '')


class WhenSamplingAProcess(unittest.TestCase):
    def test_it_should_record_every_drm_kind_beside_the_total(self):
        self.assertLessEqual({'gpu_shared_kib', 'gpu_resident_kib', 'gpu_purgeable_kib', 'gpu_active_kib',
                              'gpu_regions'}, set(perf.SAMPLE_FIELDS))


XWININFO = """
xwininfo: Window id: 0x4c00020 "Botropolis"

  Absolute upper-left X:  0
  Absolute upper-left Y:  18
  Width: 1918
  Height: 1180
  Depth: 24
  Map State: IsViewable
"""


class WhenReadingAWindowSize(unittest.TestCase):
    def test_it_should_give_width_by_height(self):
        self.assertEqual(perf.xwininfo_size(XWININFO), '1918x1180')

    def test_and_xwininfo_found_no_window_it_should_give_nothing(self):
        self.assertIsNone(perf.xwininfo_size('xwininfo: error: No such window with id 0x1.\n'))


class WhenComputingCpuPercent(unittest.TestCase):
    def test_and_a_core_is_saturated_it_should_report_one_hundred(self):
        self.assertAlmostEqual(perf.cpu_percent(0, 200, 100, 2.0), 100.0)

    def test_and_the_interval_is_zero_it_should_report_zero(self):
        self.assertEqual(perf.cpu_percent(0, 200, 100, 0.0), 0.0)


class WhenParsingProcIo(unittest.TestCase):
    def test_it_should_read_rchar_in_bytes(self):
        self.assertEqual(perf.parse_proc_io('rchar: 2048\nwchar: 1024\nread_bytes: 0\n')['rchar'], 2048)


class WhenComputingARate(unittest.TestCase):
    def test_and_two_mib_were_read_in_two_seconds_it_should_report_one_mib_a_second(self):
        self.assertAlmostEqual(perf.rate_kib_s(0, 2 * 1024 * 1024, 2.0), 1024.0)

    def test_and_the_counter_is_missing_it_should_report_none(self):
        self.assertIsNone(perf.rate_kib_s(None, 10, 1.0))


class WhenFittingASlope(unittest.TestCase):
    def test_and_memory_grows_one_mib_a_minute_it_should_report_one(self):
        xs = [0, 60, 120, 180]
        ys = [100, 101, 102, 103]
        self.assertAlmostEqual(perf.slope_per_minute(xs, ys), 1.0)

    def test_and_there_is_one_point_it_should_report_none(self):
        self.assertIsNone(perf.slope_per_minute([0], [1]))


class WhenTakingPercentiles(unittest.TestCase):
    def test_it_should_return_the_median_of_an_odd_list(self):
        self.assertEqual(perf.percentile([5, 1, 3], 50), 3)

    def test_it_should_return_the_max_at_one_hundred(self):
        self.assertEqual(perf.percentile([5, 1, 3], 100), 5)


class WhenParsingGctrace(unittest.TestCase):
    LINE = 'gc 12 @3.456s 2%: 0.1+1.2+0.01 ms clock, 0.8+0.5/2.1/0+0.1 ms cpu, 48->52->20 MB, 50 MB goal, 0 MB stacks, 0 MB globals, 16 P'

    def setUp(self):
        self.parsed = perf.parse_gctrace_line(self.LINE)

    def test_it_should_read_the_elapsed_seconds(self):
        self.assertAlmostEqual(self.parsed['at_s'], 3.456)

    def test_it_should_read_the_live_heap_after_collection(self):
        self.assertEqual(self.parsed['live_mb'], 20)

    def test_it_should_read_the_heap_goal(self):
        self.assertEqual(self.parsed['goal_mb'], 50)

    def test_and_the_line_is_not_a_gc_line_it_should_return_none(self):
        self.assertIsNone(perf.parse_gctrace_line('FRAME 120 2.3 ms'))


class WhenSummarisingSamples(unittest.TestCase):
    def setUp(self):
        rows = [
            {'elapsed_s': '0', 'comm': 'botropolis', 'pid': '1', 'cpu_pct': '10', 'private_dirty_kib': '102400', 'pss_kib': '204800', 'swap_kib': '0', 'gpu_kib': '1024', 'threads': '20', 'fds': '30'},
            {'elapsed_s': '60', 'comm': 'botropolis', 'pid': '1', 'cpu_pct': '30', 'private_dirty_kib': '112640', 'pss_kib': '215040', 'swap_kib': '0', 'gpu_kib': '1024', 'threads': '20', 'fds': '30'},
        ]
        self.summary = perf.summarise(rows)['botropolis']

    def test_it_should_average_the_cpu(self):
        self.assertAlmostEqual(self.summary['cpu_pct']['mean'], 20.0)

    def test_it_should_report_the_last_private_dirty_in_mib(self):
        self.assertAlmostEqual(self.summary['private_dirty_mib']['last'], 110.0)

    def test_it_should_report_the_private_dirty_growth_per_minute(self):
        self.assertAlmostEqual(self.summary['private_dirty_mib']['slope_per_min'], 10.0)


class WhenTrackingIdleness(unittest.TestCase):
    def setUp(self):
        self.idle = perf.IdleClock(threshold_pct=1.0, needed_s=60)

    def test_and_cpu_stays_low_long_enough_it_should_be_idle(self):
        self.idle.observe(0, 0.5)
        self.idle.observe(61, 0.2)
        self.assertTrue(self.idle.idle())

    def test_and_cpu_rises_in_between_it_should_start_over(self):
        self.idle.observe(0, 0.5)
        self.idle.observe(30, 50.0)
        self.idle.observe(61, 0.2)
        self.assertFalse(self.idle.idle())

    def test_and_it_has_only_just_gone_quiet_it_should_not_be_idle(self):
        self.idle.observe(0, 0.5)
        self.assertFalse(self.idle.idle())


class WhenSummarisingByPid(unittest.TestCase):
    def test_it_should_key_each_process_by_name_and_pid(self):
        rows = [
            {'elapsed_s': '0', 'comm': 'botropolisd', 'pid': '1', 'cpu_pct': '10'},
            {'elapsed_s': '0', 'comm': 'botropolisd', 'pid': '2', 'cpu_pct': '20'},
        ]
        self.assertEqual(sorted(perf.summarise(rows, by_pid=True)), ['botropolisd[1]', 'botropolisd[2]'])


I3_TREE = {'window': None, 'nodes': [
    {'window': None, 'nodes': [{'window': 11, 'nodes': [], 'floating_nodes': []}], 'floating_nodes': [
        {'window': None, 'nodes': [{'window': 22, 'nodes': [], 'floating_nodes': []}], 'floating_nodes': []}]},
], 'floating_nodes': []}


class WhenListingI3Windows(unittest.TestCase):
    def test_it_should_find_tiled_and_floating_windows(self):
        self.assertEqual(sorted(perf.i3_window_ids(I3_TREE)), [11, 22])


class WhenDescribingTheDesk(unittest.TestCase):
    def test_and_the_state_directory_has_no_sessions_file_it_should_exit_zero(self):
        with tempfile.TemporaryDirectory() as home:
            os.makedirs(os.path.join(home, 'state', 'botropolis'))
            env = dict(os.environ, HOME=home, XDG_STATE_HOME=os.path.join(home, 'state'))
            done = subprocess.run([os.path.join(HERE, 'perf-env')], env=env, capture_output=True)
        self.assertEqual(done.returncode, 0)


def write(path, text=''):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(text)


def files_under(root, links):
    found = set()
    for d, dirs, names in os.walk(root):
        for name in names + [x for x in dirs if os.path.islink(os.path.join(d, x))]:
            path = os.path.join(d, name)
            if os.path.islink(path) == links:
                found.add(os.path.relpath(path, root))
    return found


class WhenBuildingABusyHome(unittest.TestCase):
    def setUp(self):
        top = tempfile.TemporaryDirectory()
        self.addCleanup(top.cleanup)
        self.real = os.path.join(top.name, 'real', '.claude')
        self.home = os.path.join(top.name, 'busy')
        write(os.path.join(self.real, 'projects', '-p', 'a.jsonl'), '{}\n')
        write(os.path.join(self.real, 'projects', '-p', 'b.jsonl'), '{}\n')
        write(os.path.join(self.real, 'projects', '-p', 'a', 'subagents', 'agent-x.jsonl'), '{}\n')
        write(os.path.join(self.real, 'sessions', '1.json'), '{}')
        write(os.path.join(self.real, 'history.jsonl'), '{}\n')
        write(os.path.join(self.home, '.claude', 'projects', '-demo', 'd.jsonl'), '{}\n')
        write(os.path.join(self.home, '.claude', 'sessions', '2.json'), '{}')
        perf.busy_home(self.real, self.home)
        self.claude = os.path.join(self.home, '.claude')

    def test_it_should_link_every_transcript_and_its_subagents(self):
        self.assertEqual(files_under(os.path.join(self.claude, 'projects'), links=True),
                         {'-p/a.jsonl', '-p/b.jsonl', '-p/a'})

    def test_it_should_copy_nothing_from_the_real_home(self):
        self.assertEqual(files_under(self.claude, links=False), {'projects/-demo/d.jsonl', 'sessions/2.json'})

    def test_it_should_link_the_session_records(self):
        self.assertTrue(os.path.islink(os.path.join(self.claude, 'sessions', '1.json')))

    def test_it_should_link_the_prompt_history(self):
        self.assertTrue(os.path.islink(os.path.join(self.claude, 'history.jsonl')))


class WhenReplaying(unittest.TestCase):
    def setUp(self):
        top = tempfile.TemporaryDirectory()
        self.addCleanup(top.cleanup)
        self.top = top.name
        self.claude = os.path.join(top.name, 'home', '.claude')
        write(os.path.join(self.claude, 'sessions', '1.json'), '{"sessionId": "s1", "cwd": "/w/one"}')
        write(os.path.join(self.claude, 'projects', '-w-one', 's1.jsonl'), '{}\n')
        real = os.path.join(top.name, 'real.jsonl')
        write(real, '{}\n')
        write(os.path.join(top.name, 'real-session.json'), '{"sessionId": "s2", "cwd": "/w/two"}')
        os.makedirs(os.path.join(self.claude, 'projects', '-w-two'))
        os.symlink(real, os.path.join(self.claude, 'projects', '-w-two', 's2.jsonl'))
        os.symlink(os.path.join(top.name, 'real-session.json'), os.path.join(self.claude, 'sessions', '2.json'))
        self.real = real

    def test_it_should_only_target_the_scratch_homes_own_live_transcripts(self):
        self.assertEqual([t[0] for t in perf.replay_targets(os.path.join(self.top, 'home'))], ['s1'])

    def test_and_the_transcript_is_a_symlink_it_should_refuse_to_write(self):
        with self.assertRaises(PermissionError):
            perf.append_line(os.path.join(self.claude, 'projects', '-w-two', 's2.jsonl'), {'type': 'user'})

    def test_and_the_transcript_is_a_symlink_it_should_leave_the_target_untouched(self):
        try:
            perf.append_line(os.path.join(self.claude, 'projects', '-w-two', 's2.jsonl'), {'type': 'user'})
        except PermissionError:
            pass
        with open(self.real) as f:
            self.assertEqual(f.read(), '{}\n')

    def test_it_should_write_a_user_prompt_for_the_session(self):
        line = perf.replay_line('s1', '/w/one', 3, '2026-10-22T12:00:00Z')
        self.assertEqual((line['type'], line['sessionId'], line['cwd'], line['message']['role']), ('user', 's1', '/w/one', 'user'))

    def test_it_should_stamp_the_line_with_the_time_given(self):
        self.assertEqual(perf.replay_line('s1', '/w/one', 3, '2026-10-22T12:00:00Z')['timestamp'], '2026-10-22T12:00:00Z')

    def test_and_a_line_is_appended_it_should_be_one_json_line(self):
        path = os.path.join(self.claude, 'projects', '-w-one', 's1.jsonl')
        perf.append_line(path, perf.replay_line('s1', '/w/one', 0, '2026-10-22T12:00:00Z'))
        with open(path) as f:
            self.assertEqual(json.loads(f.read().splitlines()[-1])['sessionId'], 's1')


def sample(epoch, comm, pid, private_dirty_mib, gpu_mib):
    return {
        'ts': perf.datetime.datetime.fromtimestamp(epoch).isoformat(timespec='seconds'),
        'comm': comm, 'pid': str(pid),
        'private_dirty_kib': str(private_dirty_mib * 1024), 'gpu_kib': str(gpu_mib * 1024),
    }


class WhenSummingAPhase(unittest.TestCase):
    START = 1_800_000_000

    def setUp(self):
        s = self.START
        self.rows = [
            sample(s - 5, 'botropolis', 10, 900, 900),
            sample(s, 'botropolis', 10, 100, 200),
            sample(s, 'botropolis', 11, 5, 0),
            sample(s, 'botropolisd', 20, 50, 0),
            sample(s + 1, 'botropolis', 10, 120, 250),
            sample(s + 2, 'botropolis', 10, 110, 210),
            sample(s + 20, 'botropolis', 10, 900, 900),
        ]
        self.summary = perf.phase_summary(self.rows, s, s + 10)

    def test_it_should_add_private_dirty_and_gpu_for_the_citys_processes_at_each_sample(self):
        self.assertEqual(perf.phase_samples(self.rows, self.START, self.START + 1), [305])

    def test_and_a_sample_is_the_daemons_it_should_leave_it_out(self):
        self.assertNotIn(355, perf.phase_samples(self.rows, self.START, self.START + 1))

    def test_and_a_sample_falls_outside_the_phase_it_should_leave_it_out(self):
        self.assertEqual(len(perf.phase_samples(self.rows, self.START, self.START + 10)), 3)

    def test_it_should_report_over_the_phase(self):
        for key, want in (('least', 305), ('most', 370), ('mean', (305 + 370 + 320) / 3)):
            with self.subTest('it should report the %s' % key):
                self.assertAlmostEqual(self.summary[key], want)


def soak_row(elapsed, comm, pid, private_dirty_mib, gpu_mib=0):
    row = sample(1_800_000_000 + elapsed, comm, pid, private_dirty_mib, gpu_mib)
    row['elapsed_s'] = '%.1f' % elapsed
    return row


def soak_rows(city_visible=0.0, city_hidden=0.0, daemon_visible=0.0, daemon_hidden=0.0,
              hide_at=14400, end=28800, every=60, drop=300):
    rows = []
    for t in range(0, end + 1, every):
        hidden = t >= hide_at
        hours_in = (t - (hide_at if hidden else 0)) / 3600
        city = (400 - drop if hidden else 400) + hours_in * (city_hidden if hidden else city_visible)
        daemon = 30 + hours_in * (daemon_hidden if hidden else daemon_visible)
        rows.append(soak_row(t, 'botropolis', 10, city * 0.6, city * 0.4))
        rows.append(soak_row(t, 'botropolisd', 20, daemon))
        rows.append(soak_row(t, 'botropolisd', 99, 30 + t))
    return rows


SOAK_MARKS = {'hidden_at_s': '14400', 'frames_at_hide': '51000', 'daemon_pid': '20',
              'monitor_at_end': 'Monitor is On'}


class WhenFittingASlopePerHour(unittest.TestCase):
    def test_it_should_give_mib_an_hour_from_mib_samples_at_elapsed_seconds(self):
        self.assertAlmostEqual(perf.slope_per_hour([0, 1800, 3600], [10, 11, 12]), 2.0)

    def test_and_there_are_fewer_than_two_samples_it_should_give_none(self):
        self.assertIsNone(perf.slope_per_hour([0], [10]))


class WhenReadingRunMarks(unittest.TestCase):
    def setUp(self):
        self.marks = perf.read_marks('hidden_at_s=14400\nmonitor_at_end=Monitor is On\nnot a mark\n')

    def test_it_should_read_each_key_and_value(self):
        self.assertEqual(self.marks['monitor_at_end'], 'Monitor is On')

    def test_and_a_line_holds_no_equals_sign_it_should_skip_it(self):
        self.assertEqual(set(self.marks), {'hidden_at_s', 'monitor_at_end'})


class WhenSplittingASoakIntoPhases(unittest.TestCase):
    def setUp(self):
        self.phases = perf.soak_phases(SOAK_MARKS, end_s=28800, settle_s=600)

    def test_and_the_window_was_hidden_at_h_the_visible_phase_should_run_from_600_s_to_h(self):
        self.assertEqual(self.phases['visible'], (600, 14400))

    def test_and_the_window_was_hidden_at_h_the_hidden_phase_should_run_from_h_plus_600_s_to_the_end(self):
        self.assertEqual(self.phases['hidden'], (15000, 28800))

    def test_and_the_window_was_never_hidden_it_should_have_only_a_visible_phase_to_the_end(self):
        self.assertEqual(perf.soak_phases({}, end_s=28800, settle_s=600), {'visible': (600, 28800)})


class WhenTakingASoakSeries(unittest.TestCase):
    def setUp(self):
        self.rows = [soak_row(0, 'botropolis', 10, 100, 200), soak_row(0, 'botropolis', 11, 5, 0),
                     soak_row(0, 'botropolisd', 20, 30), soak_row(0, 'botropolisd', 99, 70)]

    def test_it_should_add_gpu_to_private_dirty_over_the_citys_processes(self):
        self.assertEqual(perf.soak_series(self.rows, 'city', '20'), [(0.0, 305.0)])

    def test_it_should_take_only_the_daemon_pid_it_is_given(self):
        self.assertEqual(perf.soak_series(self.rows, 'daemon', '20'), [(0.0, 30.0)])


class WhenJudgingASoak(unittest.TestCase):
    def judge(self, marks=None, **growth):
        return perf.judge_soak(soak_rows(**growth), dict(SOAK_MARKS, **(marks or {})))

    def failing(self, result):
        return {(p['process'], p['phase']) for p in result['phases'] if p['over']}

    def test_and_every_phase_grows_under_1_mib_an_hour_it_should_pass(self):
        self.assertEqual(self.judge(city_visible=0.5, city_hidden=0.5, daemon_visible=0.5, daemon_hidden=0.5)['verdict'], 'pass')

    def test_and_the_citys_hidden_phase_grows_2_mib_an_hour_it_should_fail_naming_city_hidden(self):
        self.assertEqual(self.failing(self.judge(city_hidden=2)), {('city', 'hidden')})

    def test_and_the_daemons_visible_phase_grows_2_mib_an_hour_it_should_fail_naming_daemon_visible(self):
        self.assertEqual(self.failing(self.judge(daemon_visible=2)), {('daemon', 'visible')})

    def test_and_a_phase_is_over_budget_it_should_give_the_verdict_fail(self):
        self.assertEqual(self.judge(city_hidden=2)['verdict'], 'fail')

    def test_and_memory_drops_at_the_hide_but_neither_phase_grows_it_should_pass(self):
        self.assertEqual(self.judge()['verdict'], 'pass')

    def test_it_should_judge_a_row_for_each_process_and_phase(self):
        self.assertEqual({(p['process'], p['phase']) for p in self.judge()['phases']},
                         {('city', 'visible'), ('city', 'hidden'), ('daemon', 'visible'), ('daemon', 'hidden')})

    def test_and_the_visible_phase_drew_no_frames_it_should_say_it_is_not_a_measurement(self):
        self.assertEqual(self.judge({'frames_at_hide': '0'})['verdict'], 'not a measurement')

    def test_and_the_hide_failed_it_should_say_it_is_not_a_measurement(self):
        marks = dict(SOAK_MARKS, hide_failed_at_s='14400')
        del marks['hidden_at_s']
        self.assertEqual(perf.judge_soak(soak_rows(), marks)['verdict'], 'not a measurement')

    def test_and_a_phase_holds_under_30_minutes_it_should_say_it_is_not_a_measurement(self):
        rows = soak_rows(hide_at=14400, end=15600)
        self.assertEqual(perf.judge_soak(rows, SOAK_MARKS)['verdict'], 'not a measurement')

    def test_and_the_monitor_was_off_at_the_end_it_should_say_it_is_not_a_measurement(self):
        self.assertEqual(self.judge({'monitor_at_end': 'Monitor is Off'})['verdict'], 'not a measurement')

    def test_and_the_monitor_went_unchecked_it_should_say_it_is_not_a_measurement(self):
        marks = dict(SOAK_MARKS)
        del marks['monitor_at_end']
        self.assertEqual(perf.judge_soak(soak_rows(), marks)['verdict'], 'not a measurement')


def stepped_rows(step_at=None, private_dirty=16, gpu=32, noise=0.0, end=7200, every=10):
    rows = []
    for t in range(0, end + 1, every):
        wobble = noise if (t // every) % 2 else -noise
        after = step_at is not None and t >= step_at
        rows.append(soak_row(t, 'botropolis', 10, 200 + wobble + (private_dirty if after else 0),
                             100 + (gpu if after else 0)))
        rows.append(soak_row(t, 'botropolisd', 20, 30))
    return rows


STEP_PHASES = {'visible': (600, 7200)}


class WhenFindingSoakSteps(unittest.TestCase):
    def steps(self, **kwargs):
        return perf.soak_steps(stepped_rows(**kwargs), STEP_PHASES, '20')

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_find_one_step(self):
        self.assertEqual(len(self.steps(step_at=3600)), 1)

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_place_it_at_that_sample(self):
        self.assertEqual(self.steps(step_at=3600)[0]['at_s'], 3600)

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_name_the_process_and_phase(self):
        step = self.steps(step_at=3600)[0]
        self.assertEqual((step['process'], step['phase']), ('city', 'visible'))

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_split_its_size_into_private_dirty_and_gpu(self):
        step = self.steps(step_at=3600)[0]
        self.assertEqual((round(step['private_dirty_mib']), round(step['gpu_mib'])), (16, 32))

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_give_a_flat_slope_before_it(self):
        self.assertAlmostEqual(self.steps(step_at=3600)[0]['before_mib_h'], 0.0)

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_give_a_flat_slope_after_it(self):
        self.assertAlmostEqual(self.steps(step_at=3600)[0]['after_mib_h'], 0.0)

    def test_and_a_flat_phase_jumps_49_mib_once_it_should_give_its_time_in_utc(self):
        self.assertEqual(self.steps(step_at=3600)[0]['utc'], '2027-01-15T09:00:00Z')

    def test_and_a_phase_only_wobbles_under_8_mib_it_should_find_no_step(self):
        self.assertEqual(self.steps(noise=3), [])

    def test_and_a_jump_is_over_8_mib_but_under_four_times_the_phases_noise_it_should_find_no_step(self):
        self.assertEqual(self.steps(step_at=3600, private_dirty=12, gpu=0, noise=6), [])

    def test_and_a_jump_is_outside_every_phase_it_should_find_no_step(self):
        self.assertEqual(self.steps(step_at=300), [])


class WhenReportingASoakStep(unittest.TestCase):
    def setUp(self):
        marks = dict(SOAK_MARKS, light='night')
        rows = stepped_rows(step_at=3600)
        result = perf.judge_soak(rows, marks, settle_s=600, min_phase_s=0)
        self.report = perf.soak_report(result, marks)

    def test_it_should_name_the_light_the_run_drew(self):
        self.assertIn('Light: night', self.report)

    def test_it_should_list_the_step_in_utc(self):
        self.assertIn('2027-01-15T09:00:00Z', self.report)

    def test_it_should_count_the_step_in_its_phases_slope(self):
        result = perf.judge_soak(stepped_rows(step_at=3600), dict(SOAK_MARKS, hide='none', frames_at_end='1'),
                                 settle_s=600, min_phase_s=0)
        self.assertGreater(result['phases'][0]['slope_mib_h'], 1.0)


class WhenReportingASoakWithoutSteps(unittest.TestCase):
    def setUp(self):
        result = perf.judge_soak(stepped_rows(), SOAK_MARKS, settle_s=600, min_phase_s=0)
        self.report = perf.soak_report(result, SOAK_MARKS)

    def test_it_should_say_it_found_none(self):
        self.assertIn('No steps', self.report)

    def test_and_the_run_named_no_light_it_should_say_the_light_followed_the_clock(self):
        self.assertIn('Light: live', self.report)


class WhenAskingPerfSoakForHelp(unittest.TestCase):
    def test_it_should_offer_light(self):
        out = subprocess.run([os.path.join(HERE, 'perf-soak'), '--help'], capture_output=True, text=True).stdout
        self.assertIn('--light', out)


class WhenJudgingASoakWithTheHideTurnedOff(unittest.TestCase):
    MARKS = {'hide': 'none', 'frames_at_end': '90000', 'daemon_pid': '20', 'monitor_at_end': 'Monitor is On'}

    def judge(self, marks=None, **growth):
        return perf.judge_soak(soak_rows(hide_at=99999, **growth), dict(self.MARKS, **(marks or {})))

    def test_and_nothing_grows_it_should_pass_on_the_visible_phase_alone(self):
        self.assertEqual(self.judge()['verdict'], 'pass')

    def test_it_should_judge_only_the_visible_phase(self):
        self.assertEqual({p['phase'] for p in self.judge()['phases']}, {'visible'})

    def test_and_the_city_grows_2_mib_an_hour_it_should_fail(self):
        self.assertEqual(self.judge(city_visible=2)['verdict'], 'fail')

    def test_and_no_frames_were_drawn_by_the_end_it_should_say_it_is_not_a_measurement(self):
        self.assertEqual(self.judge({'frames_at_end': '0'})['verdict'], 'not a measurement')


if __name__ == '__main__':
    unittest.main()
