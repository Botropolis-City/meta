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


if __name__ == '__main__':
    unittest.main()
