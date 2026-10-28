import datetime
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import zoneinfo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from hetzner import (CHOSEN, CHOSEN_HOURLY, IPV6_NET, PERSONAL_KEY, PUBLIC_KEY, SECRET, SERVER_NUMBER,  # noqa: E402
                     Bench, basic, listing)
from stubs import path_without, run_in_own_group  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MACHINES = os.path.join(ROOT, 'testing', 'machines')
TOOL = os.path.join(MACHINES, 'machines')
ROBOT_REFS = ['--robot-user-ref', 'op:Test/robot/user', '--robot-password-ref', 'op:Test/robot/password']
HCLOUD_REFS = ['--hcloud-token-ref', 'op:Test/hcloud/token']
CANCELLATION = '/robot/server/%d/cancellation' % SERVER_NUMBER
ORDER = '/robot/order/server_market/transaction'
SOAK_PLAN = ['plan', 'soak'] + ROBOT_REFS
REPORT = '/home/soak/run/out/.'
NO_IPV6 = {'STUB_FAIL': 'ip:route'}
CEILING = ['--max-hours', '0.0005']
GENTLE = {'MACHINES_POLL_SECONDS': '0.05'}
BUCKET_REFS = ['--bucket-url', '{bucket}',
               '--bucket-write-id-ref', 'op:Test/bucket/write-id', '--bucket-write-secret-ref', 'op:Test/bucket/write-secret',
               '--bucket-read-id-ref', 'op:Test/bucket/read-id', '--bucket-read-secret-ref', 'op:Test/bucket/read-secret']
BERLIN = zoneinfo.ZoneInfo('Europe/Berlin')


def booking_for(t, hours=10):
    return (datetime.datetime.fromtimestamp(t + hours * 3600, BERLIN).date() + datetime.timedelta(days=1)).isoformat()


def loud_skip(case, reason):
    sys.stderr.write('\n  SKIPPED %s: %s\n' % (case.id(), reason))
    case.skipTest(reason)


class Machines(unittest.TestCase):
    argv = []
    typed = ''
    hetzner = {}
    bucket = {}
    stub_env = {}
    plan_first = False
    dedicated_key = True

    @classmethod
    def setUpClass(cls):
        cls.bench = Bench(typed=cls.typed, dedicated_key=cls.dedicated_key, bucket=cls.bucket, **cls.hetzner)
        cls.seed(cls.bench)
        if cls.plan_first:
            cls.planned = run_in_own_group([TOOL] + SOAK_PLAN, cls.bench.env(), 60)
            cls.after_plan(cls.bench.hetzner)
        cls.started = time.time()
        cls.done = run_in_own_group([TOOL] + cls.expand(cls.argv), cls.bench.env(**cls.stub_env), 60)
        cls.finished = time.time()

    @classmethod
    def seed(cls, bench):
        pass

    @classmethod
    def after_plan(cls, hetzner):
        pass

    @classmethod
    def expand(cls, argv):
        b = cls.bench
        names = {'{build}': b.build, '{stager}': b.stager, '{corpus}': b.corpus, '{script}': b.script, '{out}': b.out,
                 '{history}': b.history, '{real-history}': b.real_history, '{bucket}': b.bucket.url}
        return [names.get(a, a) for a in argv]

    @classmethod
    def tearDownClass(cls):
        cls.bench.close()

    def ssh_commands(self):
        return [' '.join(argv) for argv in self.bench.calls('ssh')]

    def launches(self):
        return [c for c in self.ssh_commands() if 'setsid' in c and 'perf-soak' in c]

    def cancellations(self):
        return self.bench.hetzner.sent('POST', CANCELLATION)

    def cancelled_now(self):
        return [r for r in self.cancellations() if r['form'].get('cancellation_date') == ['now']]

    def booked(self):
        return [r['form']['cancellation_date'][0] for r in self.cancellations()
                if r['form'].get('cancellation_date') != ['now']]

    def cancellation_steps(self):
        return [' '.join(e[1:2] + e[3:]) for e in self.sequence() if e[0] == 'robot' and e[2] == CANCELLATION
                and e[1] != 'GET']

    def machine_txt(self):
        with open(os.path.join(self.bench.out, 'machine.txt')) as f:
            return f.read()

    def results_report(self):
        with open(os.path.join(self.bench.out, 'soak.md')) as f:
            return f.read()

    def sequence(self):
        with open(os.path.join(self.bench.spy, 'sequence')) as f:
            return [json.loads(line) for line in f]

    def positions(self, match):
        return [i for i, entry in enumerate(self.sequence()) if match(entry)]

    def fetched_at(self):
        return self.positions(lambda e: e[:2] == ['bucket', 'GET'] and e[2].endswith('/report.tar.gz'))

    def cancelled_at(self):
        return self.positions(lambda e: e == ['robot', 'POST', CANCELLATION, 'now'])

    def booked_at(self):
        return self.positions(lambda e: e[:3] == ['robot', 'POST', CANCELLATION] and e[3:] != ['now'])

    def polled_at(self):
        return self.positions(lambda e: e[:2] == ['bucket', 'GET'] and e[2].endswith('/exit'))

    def first_ssh_at(self):
        return self.positions(lambda e: e[0] == 'ssh')[0]


SOAK_RUN = ['run', 'soak'] + ROBOT_REFS + BUCKET_REFS + ['--build', '{build}', '--stager', '{stager}',
                                                         '--corpus', '{corpus}', '--history', '{history}', '--out', '{out}']
WAYLAND_RUN = ['run', 'wayland'] + HCLOUD_REFS + ['--desktop', 'kde', '--script', '{script}', '--out', '{out}']


class WhenAskedForHelp(Machines):
    argv = ['--help']

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_name_every_command(self):
        self.assertTrue(all(c in self.done.stdout for c in ('plan', 'apply', 'run', 'destroy')), self.done.stdout)

    def test_it_should_name_both_machines(self):
        self.assertTrue(all(m in self.done.stdout for m in ('soak', 'wayland')), self.done.stdout)


class WhenPlanningTheSoakWithoutTokenReferences(Machines):
    argv = ['plan', 'soak']

    def test_it_should_refuse_with_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_not_resolve_any_secret(self):
        self.assertEqual(self.bench.calls('secret-run'), [])

    def test_it_should_send_nothing_to_hetzner(self):
        self.assertEqual(self.bench.hetzner.requests, [])


class WhenRunningWaylandWithoutATokenReference(Machines):
    argv = ['run', 'wayland', '--desktop', 'gnome', '--script', '{script}']

    def test_it_should_refuse_with_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_not_call_terraform(self):
        self.assertEqual(self.bench.calls('terraform'), [])


class WhenPlanningTheSoak(Machines):
    argv = SOAK_PLAN

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_hand_secret_run_the_user_reference(self):
        self.assertIn('ROBOT_USER=op:Test/robot/user', self.bench.calls('secret-run')[0])

    def test_it_should_hand_secret_run_the_password_reference(self):
        self.assertIn('ROBOT_PASSWORD=op:Test/robot/password', self.bench.calls('secret-run')[0])

    def test_it_should_authenticate_to_robot_with_the_resolved_secrets(self):
        self.assertEqual({r['auth'] for r in self.bench.hetzner.requests}, {basic(SECRET, SECRET)})

    def test_it_should_never_put_a_secret_in_any_argv(self):
        self.assertFalse([a for a in self.bench.every_argv() if SECRET in a])

    def test_it_should_print_the_chosen_listings_id(self):
        self.assertIn(str(CHOSEN), self.done.stdout)

    def test_it_should_print_its_cpu(self):
        self.assertIn('Intel Core i5-12500', self.done.stdout)

    def test_it_should_print_its_datacenter(self):
        self.assertIn('FSN1-DC4', self.done.stdout)

    def test_it_should_print_its_hourly_price(self):
        self.assertIn(CHOSEN_HOURLY, self.done.stdout)

    def test_it_should_print_its_monthly_price(self):
        self.assertIn('109.90', self.done.stdout)

    def test_it_should_print_its_setup_fee(self):
        self.assertIn('setup fee EUR 0.00', self.done.stdout)

    def test_it_should_send_one_test_order(self):
        self.assertEqual(len(self.bench.hetzner.orders(test=True)), 1)

    def test_it_should_send_the_test_order_for_the_chosen_listing(self):
        self.assertEqual(self.bench.hetzner.orders(test=True)[0]['form'].get('product_id'), [str(CHOSEN)])

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])

    def test_it_should_put_no_private_key_in_any_argv_form_or_file_it_writes(self):
        self.assertEqual(self.bench.leaks(), [])

    def test_it_should_order_without_the_paid_ipv4_addon(self):
        self.assertNotIn('addon[]', self.bench.hetzner.orders(test=True)[0]['form'])


class WhenPlanningTheSoakAndRobotDoesNotHaveTheKey(Machines):
    argv = SOAK_PLAN
    hetzner = {'key_known': False}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_upload_the_key_before_the_test_order(self):
        paths = [r['path'] for r in self.bench.hetzner.requests if r['method'] == 'POST']
        self.assertEqual(paths, ['/robot/key', ORDER])

    def test_it_should_upload_the_dedicated_keys_public_half(self):
        self.assertEqual(self.bench.uploaded_keys(), [PUBLIC_KEY.strip()])


class WhenPlanningTheSoakAndTheDedicatedKeyIsMissing(Machines):
    argv = SOAK_PLAN
    hetzner = {'key_known': False}
    dedicated_key = False

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_create_the_dedicated_key(self):
        self.assertTrue(os.path.exists(self.bench.dedicated))

    def test_it_should_make_its_private_half_readable_by_the_user_alone(self):
        self.assertEqual(os.stat(self.bench.dedicated).st_mode & 0o777, 0o600)

    def test_it_should_give_it_no_passphrase(self):
        done = subprocess.run(['ssh-keygen', '-y', '-P', '', '-f', self.bench.dedicated], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_it_should_upload_its_public_half(self):
        with open(self.bench.dedicated + '.pub') as f:
            self.assertEqual(self.bench.uploaded_keys(), [f.read().strip()])

    def test_it_should_never_upload_the_users_personal_key(self):
        self.assertNotIn(PERSONAL_KEY.strip(), self.bench.uploaded_keys())

    def test_it_should_put_no_private_key_in_any_argv_form_or_file_it_writes(self):
        self.assertEqual(self.bench.leaks(), [])


class WhenPlanningTheSoakWithIPv4(Machines):
    argv = ['plan', 'soak', '--ipv4'] + ROBOT_REFS

    def test_it_should_order_the_ipv4_addon(self):
        self.assertEqual(self.bench.hetzner.orders(test=True)[0]['form'].get('addon[]'), ['primary_ipv4'])


class WhenPlanningTheSoakAndNoListingQualifies(Machines):
    argv = SOAK_PLAN
    hetzner = {'market': [listing(1, 'Intel Core i5-13500', '0.1200', setup='39.0000'),
                          listing(2, 'Intel Core i5-12500', None),
                          listing(3, 'AMD Ryzen 7 7700', '0.1000')]}

    def test_it_should_refuse(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_say_why(self):
        self.assertIn('1 with a setup fee, 1 with no hourly price', self.done.stderr)

    def test_it_should_send_no_order_at_all(self):
        self.assertEqual(self.bench.hetzner.sent('POST', ORDER), [])


class WhenApplyingTheSoakWithoutAPlan(Machines):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY

    def test_it_should_refuse(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenApplyingTheSoakAndTheListingIsGoneSinceThePlan(Machines):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY
    plan_first = True

    @classmethod
    def after_plan(cls, hetzner):
        hetzner.market = [p for p in hetzner.market if p['id'] != CHOSEN]

    def test_it_should_refuse(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_say_the_listing_is_gone(self):
        self.assertIn('gone', self.done.stderr)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenApplyingTheSoakAndItsHourlyPriceChangedSinceThePlan(Machines):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = '0.1690'
    plan_first = True

    @classmethod
    def after_plan(cls, hetzner):
        [p for p in hetzner.market if p['id'] == CHOSEN][0]['price_hourly'] = '0.1690'

    def test_it_should_refuse(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_say_both_prices(self):
        self.assertTrue(CHOSEN_HOURLY in self.done.stderr and '0.1690' in self.done.stderr, self.done.stderr)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenApplyingTheSoakAndTheListingNowHasASetupFee(Machines):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY
    plan_first = True

    @classmethod
    def after_plan(cls, hetzner):
        [p for p in hetzner.market if p['id'] == CHOSEN][0]['price_setup'] = '39.0000'

    def test_it_should_refuse(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenApplyingTheSoakAndTheTypedPriceDoesNotMatch(Machines):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = 'yes'
    plan_first = True

    def test_it_should_refuse(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenApplyingTheSoakAndTheTypedPriceMatches(Machines):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY
    hetzner = {'key_known': False}
    plan_first = True

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_send_one_real_order(self):
        self.assertEqual(len(self.bench.hetzner.orders(test=False)), 1)

    def test_it_should_order_the_planned_listing(self):
        self.assertEqual(self.bench.hetzner.orders(test=False)[0]['form'].get('product_id'), [str(CHOSEN)])

    def test_it_should_authorize_the_public_keys_fingerprint(self):
        self.assertEqual(self.bench.hetzner.orders(test=False)[0]['form'].get('authorized_key[]'),
                         ['bd:91:21:26:1f:fa:2a:bf:3a:ac:01:7c:ab:72:e8:82'])

    def test_and_robot_does_not_have_the_key_it_should_upload_it_first(self):
        self.assertEqual(len(self.bench.hetzner.sent('POST', '/robot/key')), 1)

    def test_it_should_not_cancel_the_server(self):
        self.assertEqual(self.cancelled_now(), [])

    def test_it_should_book_the_servers_cancellation(self):
        self.assertIn(self.booked(), [[booking_for(self.started)], [booking_for(self.finished)]])

    def test_it_should_say_how_to_destroy_it(self):
        self.assertIn('destroy', self.done.stdout)


class WhenDestroyingTheSoakWithNothingOrdered(Machines):
    argv = ['destroy', 'soak'] + ROBOT_REFS

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_cancel_nothing(self):
        self.assertEqual(self.cancelled_now(), [])


class WhenDestroyingTheSoakAfterAnApply(Machines):
    argv = ['destroy', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY

    @classmethod
    def setUpClass(cls):
        cls.bench = Bench(typed=cls.typed)
        env = cls.bench.env()
        run_in_own_group([TOOL] + SOAK_PLAN, env, 60)
        run_in_own_group([TOOL, 'apply', 'soak'] + ROBOT_REFS, env, 60)
        cls.done = run_in_own_group([TOOL] + cls.argv, env, 60)

    def test_it_should_revoke_the_booking_then_cancel_now(self):
        self.assertEqual(self.cancellation_steps()[1:], ['DELETE', 'POST now'])


class WhenRunningTheSoakAndItPasses(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_run_the_soak_on_the_box(self):
        self.assertTrue([c for c in self.ssh_commands() if 'perf-soak' in c and '192.0.2.44' in c], self.ssh_commands())

    def test_it_should_run_the_soak_on_the_boxs_display(self):
        self.assertTrue([c for c in self.ssh_commands() if 'perf-soak' in c and 'DISPLAY=:0' in c], self.ssh_commands())

    def test_it_should_book_the_cancellation_right_after_delivery_before_any_set_up(self):
        self.assertLess(self.booked_at()[0], self.first_ssh_at(), self.sequence())

    def test_it_should_book_the_day_after_the_ceiling_in_berlin(self):
        self.assertIn(self.booked(), [[booking_for(self.started)], [booking_for(self.finished)]])

    def test_it_should_record_the_booked_date(self):
        self.assertIn('cancellation booked: %s' % self.booked()[0], self.machine_txt())

    def test_it_should_record_when_the_box_was_cancelled(self):
        self.assertIn('cancelled: ', self.machine_txt())

    def test_it_should_write_the_write_key_on_the_box_through_ssh_stdin(self):
        with open(os.path.join(self.bench.spy, 'ssh-stdin')) as f:
            self.assertIn('BUCKET_SECRET=' + SECRET, f.read())

    def test_it_should_write_the_key_file_readable_by_root_alone(self):
        self.assertTrue([c for c in self.ssh_commands() if 'bucket.env' in c and 'umask 077' in c], self.ssh_commands())

    def test_it_should_never_put_a_bucket_key_in_any_argv(self):
        self.assertFalse([a for a in self.bench.every_argv() if SECRET in a])

    def test_it_should_watch_the_soak_through_the_bucket(self):
        self.assertTrue(self.bench.bucket.sent('GET', '/exit'), self.bench.bucket.requests)

    def test_it_should_fetch_the_report_from_the_bucket(self):
        self.assertEqual(self.results_report(), 'verdict from the bucket\n')

    def test_it_should_cancel_early_by_revoking_the_booking_then_cancelling_now(self):
        self.assertEqual(self.cancellation_steps()[1:], ['DELETE', 'POST now'])

    def test_it_should_start_the_soak_detached_on_the_box(self):
        self.assertTrue(self.launches(), self.ssh_commands())

    def test_it_should_start_it_once(self):
        self.assertEqual(len(self.launches()), 1, self.ssh_commands())

    def test_it_should_fetch_the_report_into_the_results(self):
        self.assertTrue(os.path.exists(os.path.join(self.bench.out, 'soak.md')), self.bench.calls('scp'))

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)

    def test_it_should_reach_the_box_with_the_dedicated_key(self):
        self.assertTrue([c for c in self.ssh_commands() if 'IdentityFile=' + self.bench.dedicated + ' ' in c + ' '],
                        self.ssh_commands())

    def test_it_should_never_use_the_users_personal_key(self):
        self.assertFalse([a for a in self.bench.every_argv() if self.bench.personal in a])

    def test_it_should_put_no_private_key_in_any_argv_form_or_file_it_writes(self):
        self.assertEqual(self.bench.leaks(), [])

    def test_it_should_set_up_in_the_rescue_system_without_rebooting(self):
        self.assertFalse([c for c in self.ssh_commands() if 'reboot' in c], self.ssh_commands())

    def test_it_should_record_the_rescue_systems_mesa_version(self):
        with open(os.path.join(self.bench.out, 'machine.txt')) as f:
            self.assertIn('mesa: 25.0.7-2', f.read())

    def test_it_should_name_the_auction_servers_cpu(self):
        with open(os.path.join(self.bench.out, 'machine.txt')) as f:
            self.assertIn('Intel Core i5-12500', f.read())

    def test_it_should_say_the_history_was_synthetic_and_how_big(self):
        with open(os.path.join(self.bench.out, 'machine.txt')) as f:
            self.assertIn('synthetic history: 3 sessions in 2 projects', f.read())

    def test_it_should_upload_the_synthetic_history(self):
        self.assertTrue([argv for argv in self.bench.calls('scp') if self.bench.history in argv], self.bench.calls('scp'))

    def test_it_should_upload_nothing_from_the_users_home(self):
        self.assertFalse([a for argv in self.bench.calls('scp') for a in argv if a.startswith(self.bench.home)])


class WhenRunningTheSoakOnTheUsersOwnHistory(Machines):
    argv = [a if a != '{history}' else '{real-history}' for a in SOAK_RUN]
    typed = CHOSEN_HOURLY

    def test_it_should_refuse_with_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_send_nothing_to_hetzner(self):
        self.assertEqual(self.bench.hetzner.requests, [])

    def test_it_should_upload_nothing(self):
        self.assertEqual(self.bench.calls('scp'), [])


class WhenRunningTheSoakAndItFails(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'exit': '1'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_still_fetch_the_report(self):
        self.assertTrue(os.path.exists(os.path.join(self.bench.out, 'soak.md')), self.bench.calls('scp'))

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndTheSetUpFails(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    stub_env = {'STUB_FAIL': 'ssh:setup'}

    def test_it_should_not_start_the_soak(self):
        self.assertFalse([c for c in self.ssh_commands() if 'perf-soak' in c])

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndRobotGivesNoIPv4(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True

    def test_it_should_reach_the_box_on_its_ipv6_nets_second_address(self):
        self.assertTrue([c for c in self.ssh_commands() if 'root@%s2' % IPV6_NET in c], self.ssh_commands())


class WhenRunningTheSoakAndItIsInterrupted(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}

    @classmethod
    def setUpClass(cls):
        cls.bench = Bench(typed=cls.typed, bucket={'exit': None}, **cls.hetzner)
        run_in_own_group([TOOL] + SOAK_PLAN, cls.bench.env(), 60)
        proc = subprocess.Popen([TOOL] + cls.expand(cls.argv), env=cls.bench.env(),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not cls.bench.bucket.sent('GET', '/exit'):
            time.sleep(0.1)
        proc.send_signal(signal.SIGINT)
        try:
            proc.communicate(timeout=30)
        finally:
            os.killpg(proc.pid, signal.SIGKILL) if proc.poll() is None else None

    def test_it_should_fetch_the_report_once(self):
        self.assertEqual(len(self.bench.bucket.sent('GET', '/report.tar.gz')), 1, self.bench.bucket.requests)

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenPlanningTheSoakAndThisMachineHasNoIPv6Route(Machines):
    argv = SOAK_PLAN
    stub_env = NO_IPV6

    def test_it_should_refuse_with_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_say_to_add_ipv4(self):
        self.assertIn('IPV4=1', self.done.stderr)

    def test_it_should_send_nothing_to_hetzner(self):
        self.assertEqual(self.bench.hetzner.requests, [])

    def test_it_should_not_resolve_any_secret(self):
        self.assertEqual(self.bench.calls('secret-run'), [])


class WhenPlanningTheSoakWithIPv4AndThisMachineHasNoIPv6Route(Machines):
    argv = ['plan', 'soak', '--ipv4'] + ROBOT_REFS
    stub_env = NO_IPV6

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)


class WhenRunningTheSoakAndThisMachineHasNoIPv6Route(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    stub_env = NO_IPV6

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenRunningTheSoakWithoutBucketReferences(Machines):
    argv = [a for a in SOAK_RUN if a not in BUCKET_REFS]
    typed = CHOSEN_HOURLY
    plan_first = True

    def test_it_should_refuse_with_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenRunningTheSoakAndTheLaptopCannotReachTheBoxOnceItRuns(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'exit_after': 2}
    stub_env = {'STUB_FAIL': 'scp:' + REPORT}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_see_it_finish_through_the_bucket(self):
        self.assertEqual(len(self.bench.bucket.sent('GET', '/exit')), 3, self.bench.bucket.requests)

    def test_it_should_fetch_the_report_from_the_bucket(self):
        self.assertEqual(self.results_report(), 'verdict from the bucket\n')

    def test_it_should_cancel_the_server_once(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndAnHourlyFetchComesRoundWhileItRuns(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'exit_after': 2}
    stub_env = {'MACHINES_FETCH_SECONDS': '0'}

    def test_it_should_fetch_the_report_before_the_soak_finishes(self):
        self.assertLess(self.fetched_at()[0], self.polled_at()[-1], self.sequence())


class WhenRunningTheSoakAndTheBucketFetchFailsThenSucceeds(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'fail_reports': 2}
    stub_env = {'STUB_FAIL': 'scp:' + REPORT}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_try_the_fetch_three_times(self):
        self.assertEqual(len(self.fetched_at()), 3, self.sequence())

    def test_it_should_cancel_only_after_the_fetch_succeeded(self):
        self.assertGreater(self.cancelled_at()[0], self.fetched_at()[2], self.sequence())


class WhenRunningTheSoakAndTheBucketFetchFailsAtTheEnd(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'fail_reports': -1}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_fall_back_to_fetching_from_the_box(self):
        self.assertEqual(self.results_report(), 'verdict\n')


class WhenRunningTheSoakAndTheFetchNeverSucceedsBeforeTheCeiling(Machines):
    argv = SOAK_RUN + ['--max-hours', '0.003']
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'fail_reports': -1}
    stub_env = dict(GENTLE, STUB_FAIL='scp:' + REPORT)

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_retry_the_fetch(self):
        self.assertGreater(len(self.fetched_at()), 1, self.sequence())

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)

    def test_it_should_say_the_report_was_lost(self):
        self.assertIn('lost', self.done.stderr)


class WhenRunningTheSoakAndItNeverFinishesBeforeTheCeiling(Machines):
    argv = SOAK_RUN + CEILING
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    bucket = {'exit': None}
    stub_env = GENTLE

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_say_the_ceiling_was_reached(self):
        self.assertIn('ceiling', self.done.stderr)

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndTheCeilingPassedBeforeTheFirstLookAtAnEndedSoak(Machines):
    argv = SOAK_RUN + ['--max-hours', '0.00001']
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}

    def test_it_should_exit_with_the_soaks_code(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_fetch_the_report_from_the_bucket(self):
        self.assertEqual(self.results_report(), 'verdict from the bucket\n')

    def test_it_should_cancel_the_server_once(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndRobotsEarliestCancellationIsLaterThanWanted(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44', 'earliest': '2099-12-31'}

    def test_it_should_book_the_earliest_date_robot_allows(self):
        self.assertEqual(self.booked(), ['2099-12-31'])

    def test_it_should_say_so(self):
        self.assertIn('2099-12-31', self.done.stdout)


class WhenRunningTheSoakAndRobotRefusesToRevokeTheBooking(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44', 'revoke_refused': True}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_say_loudly_the_box_runs_to_its_booked_date(self):
        self.assertIn('RUNS UNTIL ITS BOOKED CANCELLATION ON %s' % self.booked()[0], self.done.stderr)

    def test_it_should_say_what_that_costs(self):
        self.assertIn('EUR', self.done.stderr.split('BOOKED CANCELLATION', 1)[-1])


PERF_COPY = 'run/performance'
SET_UP = 'bash /root/setup /root/botropolis'
DIAGNOSTICS = ['/root/setup.log', 'dri.txt', '/var/log/soak-xorg.out', '/var/log/Xorg.0.log', '/home/soak/i3.log',
               'dmesg', 'ip addr', 'free -m', 'ps aux']
KEEP = ['--keep-on-failure']


class SoakBox(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}

    def ssh_at(self, word):
        return self.positions(lambda e: e[0] == 'ssh' and word in e[-1])

    def scp_at(self, word):
        return self.positions(lambda e: e[0] == 'scp' and any(word in a for a in e[1:]))

    def copies(self, word):
        return [argv for argv in self.bench.calls('scp') if any(word in a for a in argv)]

    def diagnostics(self):
        return [c for c in self.ssh_commands() if 'setup.log' in c and 'dmesg' in c]

    def diagnostics_at(self):
        return self.positions(lambda e: e[0] == 'ssh' and 'setup.log' in e[-1] and 'dmesg' in e[-1])

    def streams(self):
        return [c for c in self.ssh_commands() if 'dmesg --follow' in c]

    def box_log(self):
        with open(os.path.join(self.bench.out, 'box.log')) as f:
            return f.read()


class WhenRunningTheSoakAndTheCopyTimesOutTwiceThenSucceeds(SoakBox):
    stub_env = {'STUB_SEQ': 'scp:%s=255|255|0' % PERF_COPY}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_try_that_copy_three_times(self):
        self.assertEqual(len(self.copies(PERF_COPY)), 3, self.bench.calls('scp'))

    def test_it_should_start_the_soak_once(self):
        self.assertEqual(len(self.launches()), 1, self.ssh_commands())


class WhenRunningTheSoakAndTheCopyKeepsTimingOut(SoakBox):
    stub_env = {'STUB_SEQ': 'scp:%s=255' % PERF_COPY}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_try_that_copy_five_times(self):
        self.assertEqual(len(self.copies(PERF_COPY)), 5, self.bench.calls('scp'))

    def test_it_should_not_start_the_soak(self):
        self.assertEqual(self.launches(), [])

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)

    def test_it_should_ping_the_box(self):
        self.assertTrue([argv for argv in self.bench.calls('ping') if '192.0.2.44' in argv], self.bench.calls('ping'))

    def test_it_should_collect_every_diagnostic_from_the_box(self):
        for item in DIAGNOSTICS:
            with self.subTest(item=item):
                self.assertTrue([c for c in self.diagnostics() if item in c], self.ssh_commands())

    def test_it_should_collect_them_before_cancelling(self):
        self.assertLess(self.diagnostics_at()[0], self.cancelled_at()[0], self.sequence())

    def test_it_should_say_what_it_could_not_collect(self):
        self.assertIn('could not collect the diagnostics', self.done.stderr)


class WhenRunningTheSoakWithAnAttemptBudgetOfThree(SoakBox):
    stub_env = {'STUB_SEQ': 'scp:%s=255' % PERF_COPY, 'MACHINES_SSH_ATTEMPTS': '3'}

    def test_it_should_try_that_copy_three_times(self):
        self.assertEqual(len(self.copies(PERF_COPY)), 3, self.bench.calls('scp'))


class WhenRunningTheSoakAndARemoteCommandFailsWithItsOwnExitCode(SoakBox):
    stub_env = {'STUB_SEQ': 'ssh:bucket.env=1'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_try_it_once(self):
        self.assertEqual(len(self.ssh_at('bucket.env')), 1, self.ssh_commands())

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndTheSetUpDropsItsConnectionOnce(SoakBox):
    stub_env = {'STUB_SEQ': 'ssh:%s=255|0' % SET_UP}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_run_the_set_up_again(self):
        self.assertEqual(len(self.ssh_at(SET_UP)), 2, self.ssh_commands())


class WhenRunningTheSoakAndTheDetachedStartDropsItsConnectionOnce(SoakBox):
    stub_env = {'STUB_SEQ': 'ssh:setsid=255|0'}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_guard_every_start_so_the_soak_starts_at_most_once(self):
        self.assertEqual([c for c in self.launches() if 'mkdir /root/soak.started' in c], self.launches())


class WhenRunningTheSoakAndTheSetUpHasFinished(SoakBox):
    def test_it_should_wait_for_ssh_to_answer_before_copying(self):
        answered = [i for i in self.positions(lambda e: e[0] == 'ssh' and e[-1] == 'true')
                    if i > self.ssh_at(SET_UP)[0]]
        self.assertLess(answered[0], self.scp_at(PERF_COPY)[0], self.sequence())


class WhenRunningTheSoakAndTheBoxSpeaksWhileItIsSetUp(SoakBox):
    stub_env = {'STUB_SEQ': 'ssh:dmesg --follow=0:[ 1.0] i915 0000-00-02.0 forced DP-1'}

    def test_it_should_stream_its_kernel_log_into_box_log(self):
        self.assertIn('i915 0000-00-02.0 forced DP-1', self.box_log())

    def test_it_should_stream_a_heartbeat_too(self):
        self.assertTrue([c for c in self.streams() if 'heartbeat' in c and 'loadavg' in c], self.ssh_commands())

    def test_it_should_start_the_stream_before_the_set_up(self):
        self.assertLess(self.ssh_at('dmesg --follow')[0], self.ssh_at(SET_UP)[0], self.sequence())


class WhenRunningTheSoakAndTheStreamNeverEnds(SoakBox):
    stub_env = {'STUB_HANG': 'ssh:dmesg --follow'}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and any(cls.alive(p) for p in cls.bench.hung()):
            time.sleep(0.1)

    @staticmethod
    def alive(pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_stop_the_stream_once_the_soak_has_started(self):
        self.assertEqual([p for p in self.bench.hung() if self.alive(p)], [])


class WhenRunningTheSoakAndItPassesWithItsStream(SoakBox):
    def test_it_should_open_one_stream(self):
        self.assertEqual(len(self.streams()), 1, self.ssh_commands())

    def test_it_should_collect_no_diagnostics(self):
        self.assertEqual(self.diagnostics_at(), [])


class WhenRunningTheSoakToKeepOnFailureAndTheCopyFailsForGood(SoakBox):
    argv = SOAK_RUN + KEEP
    stub_env = {'STUB_SEQ': 'scp:%s=255' % PERF_COPY}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_not_cancel_the_server(self):
        self.assertEqual(self.cancelled_now(), [])

    def test_it_should_leave_the_booked_cancellation_in_place(self):
        self.assertEqual(self.cancellation_steps(), ['POST %s' % self.booked()[0]])

    def test_it_should_say_the_booked_date(self):
        self.assertIn(self.booked()[0], self.done.stderr.split('KEPT', 1)[-1])

    def test_it_should_say_the_most_it_costs(self):
        self.assertIn('EUR', self.done.stderr.split('KEPT', 1)[-1])

    def test_it_should_say_how_to_reach_the_box(self):
        self.assertIn('ssh -i %s root@192.0.2.44' % self.bench.dedicated, self.done.stderr)

    def test_it_should_say_how_to_destroy_it(self):
        self.assertIn('make destroy MACHINE=soak', self.done.stderr.split('KEPT', 1)[-1])

    def test_it_should_record_that_it_was_kept(self):
        self.assertIn('kept on failure', self.machine_txt())

    def test_it_should_still_collect_the_diagnostics(self):
        self.assertTrue(self.diagnostics_at(), self.sequence())


class WhenRunningTheSoakToKeepOnFailureAndItPasses(SoakBox):
    argv = SOAK_RUN + KEEP

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakToKeepOnFailureAndItIsInterrupted(WhenRunningTheSoakAndItIsInterrupted):
    argv = SOAK_RUN + KEEP


PREFLIGHT = 'perf-soak --preflight'
SOAK_RUNTIME = 'XDG_RUNTIME_DIR=/run/soak'


class WhenRunningTheSoakItPreflightsTheBox(SoakBox):
    def preflights(self):
        return [c for c in self.ssh_commands() if PREFLIGHT in c]

    def test_it_should_run_the_pre_flight_as_the_soak_user(self):
        self.assertIn('runuser -u soak', self.preflights()[0], self.ssh_commands())

    def test_it_should_run_the_pre_flight_on_the_boxs_display(self):
        self.assertIn('DISPLAY=:0', self.preflights()[0], self.ssh_commands())

    def test_it_should_run_the_pre_flight_after_copying_the_tools(self):
        self.assertGreater(self.ssh_at(PREFLIGHT)[0], self.scp_at(PERF_COPY)[0], self.sequence())

    def test_it_should_run_the_pre_flight_before_starting_the_soak(self):
        self.assertLess(self.ssh_at(PREFLIGHT)[0], self.ssh_at('setsid')[0], self.sequence())

    def test_it_should_record_that_the_pre_flight_passed(self):
        self.assertIn('pre-flight: passed', self.machine_txt())

    def test_it_should_run_the_pre_flight_with_the_soak_users_runtime_directory(self):
        self.assertIn(SOAK_RUNTIME, self.preflights()[0], self.ssh_commands())

    def test_it_should_run_the_soak_with_the_soak_users_runtime_directory(self):
        self.assertIn(SOAK_RUNTIME, self.launches()[0], self.ssh_commands())

    def test_it_should_copy_start_i3_to_the_box_with_the_set_up(self):
        self.assertTrue([argv for argv in self.copies('/soak/setup') if any(a.endswith('/soak/start-i3') for a in argv)],
                        self.bench.calls('scp'))


class WhenRunningTheSoakAndThePreFlightFails(SoakBox):
    stub_env = {'STUB_SEQ': 'ssh:--preflight=2:perf-soak: xprop is missing'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_not_start_the_soak(self):
        self.assertEqual(self.launches(), [])

    def test_it_should_try_it_once(self):
        self.assertEqual(len(self.ssh_at(PREFLIGHT)), 1, self.ssh_commands())

    def test_it_should_say_the_pre_flight_failed(self):
        self.assertIn('pre-flight failed', self.done.stderr)

    def test_it_should_say_what_the_pre_flight_said(self):
        self.assertIn('xprop is missing', self.done.stderr)

    def test_it_should_collect_the_diagnostics(self):
        self.assertTrue(self.diagnostics_at(), self.sequence())

    def collects(self, path):
        return re.search(r'(^|\s)%s(\s|;|$)' % re.escape(path), self.diagnostics()[0]) is not None

    def test_it_should_collect_the_directory_the_pre_flight_wrote_to(self):
        given = shlex.split([c for c in self.ssh_commands() if PREFLIGHT in c][0])
        self.assertTrue(self.collects(given[given.index('--out') + 1]), self.diagnostics())

    def test_it_should_collect_the_soaks_out_directory(self):
        self.assertTrue(self.collects('/home/soak/run/out'), self.diagnostics())

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakToKeepOnFailureAndThePreFlightFails(SoakBox):
    argv = SOAK_RUN + KEEP
    stub_env = WhenRunningTheSoakAndThePreFlightFails.stub_env

    def test_it_should_not_cancel_the_server(self):
        self.assertEqual(self.cancelled_now(), [])


LOCK_DOWN = 'bash -s -- --allow'


class LockDown(SoakBox):
    def answered_at(self):
        return self.positions(lambda e: e[0] == 'ssh' and e[-1] == 'true')[0]

    def lock_downs(self):
        return [c for c in self.ssh_commands() if LOCK_DOWN in c]

    def after_lock_down(self):
        start = self.ssh_at(LOCK_DOWN)[0]
        return [e for e in self.sequence()[start + 1:] if e[0] in ('ssh', 'scp')]


class WhenRunningTheSoakItLocksDownSsh(LockDown):
    def test_it_should_ask_the_box_where_the_runner_connects_from_once_it_answers(self):
        self.assertEqual(self.ssh_at('SSH_CLIENT')[0], self.answered_at() + 1, self.sequence())

    def test_it_should_lock_down_next(self):
        self.assertEqual(self.ssh_at(LOCK_DOWN)[0], self.ssh_at('SSH_CLIENT')[0] + 1, self.sequence())

    def test_it_should_open_port_22_to_the_runners_address_alone(self):
        self.assertEqual(self.lock_downs(), [c for c in self.lock_downs() if c.endswith('--allow 198.51.100.7/32')])

    def test_it_should_lock_down_once(self):
        self.assertEqual(len(self.lock_downs()), 1, self.ssh_commands())

    def test_it_should_lock_down_before_the_box_streams_or_is_set_up(self):
        self.assertLess(self.ssh_at(LOCK_DOWN)[0], min(self.ssh_at('dmesg --follow')[0], self.scp_at('setup')[0]),
                        self.sequence())

    def test_it_should_send_the_lock_down_script_on_ssh_stdin(self):
        with open(os.path.join(MACHINES, 'soak', 'lockdown')) as script, \
                open(os.path.join(self.bench.spy, 'ssh-stdin')) as sent:
            self.assertIn(script.read(), sent.read())

    def test_it_should_record_who_may_reach_the_box(self):
        self.assertIn('ssh: open to 198.51.100.7/32 alone, with no passwords', self.machine_txt())

    def test_it_should_share_one_connection_for_every_ssh_and_scp_after_it(self):
        self.assertEqual([e for e in self.after_lock_down() if not any(a.startswith('ControlPath=') for a in e)], [])

    def test_it_should_let_the_first_connection_become_the_shared_one(self):
        self.assertEqual([e for e in self.after_lock_down() if 'ControlMaster=auto' not in e], [])

    def test_it_should_close_the_shared_connection_at_the_end(self):
        self.assertTrue([argv for argv in self.bench.calls('ssh') if argv[-3:-1] == ['-O', 'exit']],
                        self.bench.calls('ssh'))


class WhenRunningTheSoakFromAnIPv6Address(LockDown):
    stub_env = {'STUB_SEQ': 'ssh:SSH_CLIENT=0:2001:db8:5:6:a:b:c:d 53122 22'}

    def test_it_should_open_port_22_to_the_runners_slash_64(self):
        self.assertTrue(self.lock_downs()[0].endswith('--allow 2001:db8:5:6::/64'), self.lock_downs())


class WhenRunningTheSoakAndTheBoxCannotSayWhereTheRunnerConnectsFrom(LockDown):
    stub_env = {'STUB_SEQ': 'ssh:SSH_CLIENT=0:'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_not_set_up_the_box(self):
        self.assertEqual(self.ssh_at(SET_UP), [])

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndTheLockDownFails(LockDown):
    stub_env = {'STUB_SEQ': 'ssh:%s=1' % LOCK_DOWN}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_try_it_once(self):
        self.assertEqual(len(self.lock_downs()), 1, self.ssh_commands())

    def test_it_should_not_set_up_the_box(self):
        self.assertEqual(self.ssh_at(SET_UP), [])

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.cancelled_now()), 1)


class WhenRunningTheSoakAndTheLockDownDropsItsConnectionOnce(LockDown):
    stub_env = {'STUB_SEQ': 'ssh:%s=255|0' % LOCK_DOWN}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_try_it_again(self):
        self.assertEqual(len(self.lock_downs()), 2, self.ssh_commands())


FIREWALL_TOOLS = ('nft', 'iptables', 'ip6tables', 'iptables-legacy', 'ip6tables-legacy', 'sshd', 'systemctl')
RECORDING = '#!/usr/bin/env bash\necho "$(basename "$0") $*" >>"$LOCKDOWN_SPY"\n'


class LockingDownABox(unittest.TestCase):
    tools = ('nft', 'iptables', 'ip6tables', 'iptables-legacy', 'ip6tables-legacy')
    allow = '198.51.100.7/32'

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.spy = os.path.join(cls.top, 'spy')
        cls.config = os.path.join(cls.top, 'sshd_config')
        with open(cls.config, 'w') as f:
            f.write('Port 22\n')
        bin = path_without(FIREWALL_TOOLS, os.path.join(cls.top, 'bin'),
                           {t: RECORDING for t in cls.tools + ('sshd', 'systemctl')})
        cls.done = subprocess.run(['bash', os.path.join(MACHINES, 'soak', 'lockdown'), '--allow', cls.allow],
                                  env=dict(os.environ, PATH=bin, LOCKDOWN_SPY=cls.spy, SSHD_CONFIG=cls.config),
                                  capture_output=True, text=True, timeout=60)
        try:
            with open(cls.spy) as f:
                cls.calls = f.read().splitlines()
        except OSError:
            cls.calls = []
        with open(cls.config) as f:
            cls.configured = f.read()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.top, ignore_errors=True)

    def used(self, tool):
        return [c for c in self.calls if c.split()[0] == tool]


class WhenLockingDownABoxThatHasLegacyIptablesAndNft(LockingDownABox):
    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_accept_the_runner_first_with_legacy_iptables(self):
        self.assertIn('iptables-legacy -I INPUT 1 -p tcp --dport 22 -s 198.51.100.7/32 -j ACCEPT', self.calls)

    def test_it_should_drop_everyone_else_right_after(self):
        self.assertIn('iptables-legacy -I INPUT 2 -p tcp --dport 22 -j DROP', self.calls)

    def test_it_should_drop_port_22_over_ipv6_altogether(self):
        self.assertIn('ip6tables-legacy -I INPUT 1 -p tcp --dport 22 -j DROP', self.calls)

    def test_it_should_not_use_nft(self):
        self.assertEqual(self.used('nft'), [])

    def test_it_should_not_use_the_nft_backed_iptables(self):
        self.assertEqual(self.used('iptables') + self.used('ip6tables'), [])

    def test_it_should_turn_off_password_logins(self):
        self.assertIn('PasswordAuthentication no', self.configured)

    def test_it_should_keep_the_rest_of_sshds_configuration(self):
        self.assertIn('Port 22', self.configured)

    def test_it_should_reload_sshd(self):
        self.assertIn('systemctl reload ssh', self.calls)


class WhenLockingDownABoxForAnIPv6Runner(LockingDownABox):
    allow = '2001:db8:5:6::/64'

    def test_it_should_accept_the_runners_slash_64_with_legacy_ip6tables(self):
        self.assertIn('ip6tables-legacy -I INPUT 1 -p tcp --dport 22 -s 2001:db8:5:6::/64 -j ACCEPT', self.calls)

    def test_it_should_drop_port_22_over_ipv4_altogether(self):
        self.assertIn('iptables-legacy -I INPUT 1 -p tcp --dport 22 -j DROP', self.calls)


class WhenLockingDownABoxThatHasOnlyNft(LockingDownABox):
    tools = ('nft',)

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_use_nft(self):
        self.assertTrue(self.used('nft'), self.calls)


class WhenLockingDownABoxThatHasNoFirewall(LockingDownABox):
    tools = ()

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_leave_sshd_alone(self):
        self.assertEqual(self.configured, 'Port 22\n')


class WhenReadingTheLockDown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.join(MACHINES, 'soak', 'lockdown')
        with open(cls.path) as f:
            cls.text = f.read()

    def test_it_should_turn_off_password_logins(self):
        self.assertIn('PasswordAuthentication no', self.text)

    def test_it_should_turn_off_keyboard_interactive_logins(self):
        self.assertIn('KbdInteractiveAuthentication no', self.text)

    def test_it_should_check_sshds_configuration_before_reloading_it(self):
        self.assertIn('sshd -t', self.text)

    def test_it_should_drop_port_22_from_everyone_else(self):
        self.assertIn('dport 22 drop', self.text)

    def test_it_should_answer_help(self):
        done = subprocess.run(['bash', self.path, '--help'], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


class WhenReadingTheSetUp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(MACHINES, 'soak', 'setup')) as f:
            cls.text = f.read()

    def test_it_should_install_x11_utils_on_the_same_apt_line_as_x11_xserver_utils(self):
        apt = [c.split() for c in self.text.replace('\\\n', ' ').splitlines() if 'x11-xserver-utils' in c.split()]
        self.assertIn('x11-utils', apt[0], apt)

    def test_it_should_tee_everything_it_says_to_root_setup_log(self):
        self.assertIn('tee -a /root/setup.log', self.text)

    def test_it_should_say_each_step_after_apt(self):
        for step in ('setup: forcing', 'setup: starting Xorg', 'setup: X is up', 'setup: i3 started'):
            with self.subTest(step=step):
                self.assertIn(step, self.text)

    def test_it_should_wait_on_another_apt_rather_than_fail(self):
        self.assertIn('DPkg::Lock::Timeout', self.text)

    def test_it_should_declare_the_i3_config_as_v4_on_its_first_line(self):
        config = self.text.split("/home/soak/.config/i3/config <<'I3'\n", 1)[1]
        self.assertEqual(config.splitlines()[0], '# i3 config file (v4)')

    def test_it_should_exit_5_when_start_i3_fails(self):
        self.assertTrue([line for line in self.text.splitlines() if 'start-i3' in line and 'exit 5' in line], self.text)

    def test_it_should_start_i3_before_saying_i3_started(self):
        self.assertLess(self.text.index('/start-i3"'), self.text.index('setup: i3 started'))

    def test_it_should_run_nothing_as_soak_with_roots_runtime_directory(self):
        for script in ('setup', 'start-i3'):
            with open(os.path.join(MACHINES, 'soak', script)) as f:
                lines = [line for line in f if 'runuser -u soak' in line and 'XDG_RUNTIME_DIR=' not in line]
            with self.subTest(script=script):
                self.assertEqual(lines, [])


I3_ERROR = '[libi3] ERROR: mkdir(/run/user/0/i3) failed: Permission denied'
I3_TOOLS = ('runuser', 'i3', 'i3-msg', 'pgrep', 'install')
I3_STUBS = {
    'runuser': '#!/usr/bin/env bash\necho "runuser $*" >>"$I3_SPY/calls"\n'
               'while [[ $# -gt 0 && "$1" != -- ]]; do shift; done\nshift\nexec "$@"\n',
    'install': '#!/usr/bin/env bash\necho "install $*" >>"$I3_SPY/calls"\nmkdir -p "${@: -1}"\n',
    'pgrep': '#!/usr/bin/env bash\necho "pgrep $*" >>"$I3_SPY/calls"\n[[ "$FAKE_I3" == already ]]\n',
    'i3': '#!/usr/bin/env bash\necho "i3 $*" >>"$I3_SPY/calls"\n'
          'echo "${XDG_RUNTIME_DIR:-}" >"$I3_SPY/i3-runtime"\n'
          'if [[ "$FAKE_I3" == dies ]]; then echo "%s" >&2; echo "Segmentation fault" >&2; exit 139; fi\n'
          'touch "$I3_SPY/alive"\necho $$ >"$I3_SPY/i3-pid"\nexec sleep 30\n' % I3_ERROR,
    'i3-msg': '#!/usr/bin/env bash\necho "i3-msg $* DISPLAY=${DISPLAY:-} USER_RUNTIME=${XDG_RUNTIME_DIR:-}" >>"$I3_SPY/calls"\n'
              '[[ "$FAKE_I3" != silent && -e "$I3_SPY/alive" ]] || exit 1\necho \'{"human_readable": "4.22"}\'\n',
}


class StartingI3(unittest.TestCase):
    fake = 'up'
    wait = '10'

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.spy = os.path.join(cls.top, 'spy')
        os.makedirs(cls.spy)
        if cls.fake == 'already':
            open(os.path.join(cls.spy, 'alive'), 'w').close()
        cls.runtime = os.path.join(cls.top, 'run-soak')
        cls.log = os.path.join(cls.top, 'i3.log')
        bin = path_without(I3_TOOLS, os.path.join(cls.top, 'bin'), I3_STUBS)
        env = dict(os.environ, PATH=bin, I3_SPY=cls.spy, FAKE_I3=cls.fake, XDG_RUNTIME_DIR='/run/user/0',
                   SOAK_RUNTIME_DIR=cls.runtime, I3_LOG=cls.log, I3_WAIT_SECONDS=cls.wait)
        started = time.time()
        cls.done = subprocess.run(['bash', os.path.join(MACHINES, 'soak', 'start-i3')], env=env,
                                  capture_output=True, text=True, timeout=60)
        cls.took = time.time() - started
        cls.said = cls.done.stdout + cls.done.stderr
        cls.calls = cls.read('calls').splitlines()

    @classmethod
    def read(cls, name):
        try:
            with open(os.path.join(cls.spy, name)) as f:
                return f.read()
        except OSError:
            return ''

    @classmethod
    def tearDownClass(cls):
        pid = cls.read('i3-pid').strip()
        if pid:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except (ProcessLookupError, ValueError):
                pass
        shutil.rmtree(cls.top, ignore_errors=True)

    def used(self, tool):
        return [c for c in self.calls if c.split()[0] == tool]


class WhenStartingI3OnTheSoakBox(StartingI3):
    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.said)

    def test_it_should_give_i3_the_soak_users_runtime_directory_not_roots(self):
        self.assertEqual(self.read('i3-runtime').strip(), self.runtime)

    def test_it_should_make_that_directory_0700_and_owned_by_soak(self):
        self.assertIn('install -d -m 0700 -o soak -g soak %s' % self.runtime, self.calls)

    def test_it_should_ask_i3_msg_for_its_version_as_soak_on_display_0(self):
        self.assertTrue([c for c in self.used('i3-msg') if '-t get_version' in c and 'DISPLAY=:0' in c
                         and 'USER_RUNTIME=%s' % self.runtime in c], self.calls)

    def test_it_should_say_i3_started(self):
        self.assertIn('i3 started', self.said)


class WhenStartingI3AndItDiesAtOnce(StartingI3):
    fake = 'dies'
    wait = '20'

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_not_say_i3_started(self):
        self.assertNotIn('i3 started', self.said)

    def test_it_should_name_i3_log(self):
        self.assertIn(self.log, self.said)

    def test_it_should_quote_the_logs_last_line(self):
        self.assertIn('Segmentation fault', self.said)

    def test_it_should_give_up_before_the_wait_runs_out(self):
        self.assertLess(self.took, 10)


class WhenStartingI3AndItStaysUpButNeverAnswers(StartingI3):
    fake = 'silent'
    wait = '1'

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_wait_before_giving_up(self):
        self.assertGreaterEqual(self.took, 1)


class WhenStartingI3AndItIsAlreadyRunning(StartingI3):
    fake = 'already'

    def test_it_should_not_start_a_second_i3(self):
        self.assertEqual(self.used('i3'), [])

    def test_it_should_still_check_that_it_answers(self):
        self.assertTrue([c for c in self.used('i3-msg') if '-t get_version' in c], self.calls)


class WhenReadingStartI3(unittest.TestCase):
    def test_it_should_answer_help(self):
        done = subprocess.run(['bash', os.path.join(MACHINES, 'soak', 'start-i3'), '--help'],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


class WhenMakeRunSoakIsAskedToKeepOnFailure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.done = subprocess.run(['make', '--no-print-directory', '-n', '-C', MACHINES, 'run-soak', 'PERF_BUILD=/x',
                                   'KEEP_ON_FAILURE=1'], capture_output=True, text=True, timeout=60)

    def test_it_should_pass_keep_on_failure_to_the_runner(self):
        self.assertIn('--keep-on-failure', self.done.stdout)


class WhenPlanningWayland(Machines):
    argv = ['plan', 'wayland', '--desktop', 'kde'] + HCLOUD_REFS

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_hand_secret_run_the_token_reference(self):
        self.assertIn('HCLOUD_TOKEN=op:Test/hcloud/token', self.bench.calls('secret-run')[0])

    def test_it_should_read_the_price_with_the_resolved_token(self):
        self.assertEqual({r['auth'] for r in self.bench.hetzner.requests}, {'Bearer ' + SECRET})

    def test_it_should_print_the_hourly_price(self):
        self.assertIn('0.0090', self.done.stdout)

    def test_it_should_give_terraform_the_dedicated_public_key(self):
        self.assertTrue([argv for argv in self.bench.calls('terraform')
                         if 'ssh_public_key_file=' + self.bench.dedicated + '.pub' in argv], self.bench.calls('terraform'))

    def test_it_should_plan_the_kde_desktop(self):
        self.assertTrue([argv for argv in self.bench.calls('terraform') if 'plan' in argv and 'desktop=kde' in argv],
                        self.bench.calls('terraform'))

    def test_it_should_apply_nothing(self):
        self.assertFalse([argv for argv in self.bench.calls('terraform') if 'apply' in argv])

    def test_it_should_never_put_a_secret_in_any_argv(self):
        self.assertFalse([a for a in self.bench.every_argv() if SECRET in a])


class WhenRunningWaylandAndItPasses(Machines):
    argv = WAYLAND_RUN

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_leave_the_approval_to_terraforms_own_prompt(self):
        self.assertFalse([argv for argv in self.bench.calls('terraform') if 'apply' in argv and '-auto-approve' in argv])

    def test_it_should_run_the_script_on_the_vm(self):
        self.assertTrue([c for c in self.ssh_commands() if 'shortcut-test' in c and '2a01:4f8:c0c:1::1' in c], self.ssh_commands())

    def test_it_should_fetch_the_results(self):
        self.assertTrue([argv for argv in self.bench.calls('scp') if argv[-1] == self.bench.out], self.bench.calls('scp'))

    def test_it_should_destroy_the_vm(self):
        self.assertTrue([argv for argv in self.bench.calls('terraform') if 'destroy' in argv])


class WhenRunningWaylandAndTheScriptFails(Machines):
    argv = WAYLAND_RUN
    stub_env = {'STUB_FAIL': 'ssh:shortcut-test'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_destroy_the_vm(self):
        self.assertTrue([argv for argv in self.bench.calls('terraform') if 'destroy' in argv])


class WhenRunningWaylandAndTheApplyFails(Machines):
    argv = WAYLAND_RUN
    stub_env = {'STUB_FAIL': 'terraform:apply'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_still_destroy_whatever_was_made(self):
        self.assertTrue([argv for argv in self.bench.calls('terraform') if 'destroy' in argv])


class WhenMakePlanRunsWithoutTokenReferences(Machines):
    @classmethod
    def setUpClass(cls):
        cls.bench = Bench()
        env = cls.bench.env()
        for name in ('HCLOUD_TOKEN_REF', 'ROBOT_USER_REF', 'ROBOT_PASSWORD_REF'):
            env.pop(name, None)
        cls.done = subprocess.run(['make', '--no-print-directory', '-C', MACHINES, 'plan', 'MACHINE=soak'],
                                  env=env, capture_output=True, text=True, timeout=60)

    def test_it_should_fail(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_not_resolve_any_secret(self):
        self.assertEqual(self.bench.calls('secret-run'), [])


class WhenListingTheMakeTargets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.done = subprocess.run(['make', '--no-print-directory', '-C', MACHINES], capture_output=True, text=True, timeout=60)
        cls.targets = {line.split()[0] for line in cls.done.stdout.splitlines() if line.strip()}

    def test_it_should_offer_every_target_the_item_names(self):
        self.assertLessEqual({'plan', 'apply', 'run-soak', 'run-wayland', 'destroy', 'validate'}, self.targets)


class WhenCheckingWhatGitIgnores(unittest.TestCase):
    def ignored(self, path):
        return subprocess.run(['git', 'check-ignore', '-q', '--no-index', path], cwd=ROOT).returncode == 0

    def test_it_should_ignore_the_token_references_env_file(self):
        self.assertTrue(self.ignored('testing/machines/.env'))

    def test_it_should_ignore_terraform_state(self):
        self.assertTrue(self.ignored('testing/machines/cloud/terraform.tfstate'))

    def test_it_should_ignore_terraforms_working_directory(self):
        self.assertTrue(self.ignored('testing/machines/cloud/.terraform/providers'))

    def test_it_should_track_the_machines_makefile(self):
        self.assertFalse(self.ignored('testing/machines/Makefile'))


class WhenCheckingTheTerraform(unittest.TestCase):
    cache = os.path.join(os.environ.get('XDG_CACHE_HOME') or os.path.expanduser('~/.cache'), 'botropolis-machines', 'plugins')

    def setUp(self):
        if not shutil.which('terraform'):
            loud_skip(self, 'terraform is not installed')

    def test_it_should_be_formatted(self):
        done = subprocess.run(['terraform', 'fmt', '-check', '-recursive', os.path.join(MACHINES, 'cloud')],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_it_should_validate(self):
        if not os.path.isdir(os.path.join(self.cache, 'registry.terraform.io', 'hetznercloud', 'hcloud')):
            loud_skip(self, 'validate skipped: provider not cached (make -C testing/machines validate caches it)')
        work = tempfile.mkdtemp()
        try:
            shutil.copytree(os.path.join(MACHINES, 'cloud'), os.path.join(work, 'cloud'),
                            ignore=shutil.ignore_patterns('.terraform', '*.tfstate*'))
            env = dict(os.environ, TF_DATA_DIR=os.path.join(work, '.terraform'), TF_IN_AUTOMATION='1')
            cwd = os.path.join(work, 'cloud')
            init = subprocess.run(['terraform', 'init', '-backend=false', '-input=false', '-plugin-dir=' + self.cache],
                                  cwd=cwd, env=env, capture_output=True, text=True)
            done = init if init.returncode else subprocess.run(['terraform', 'validate'], cwd=cwd, env=env,
                                                               capture_output=True, text=True)
        finally:
            shutil.rmtree(work, ignore_errors=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


class WhenCheckingTheGuestSetUp(unittest.TestCase):
    def setUp(self):
        if not shutil.which('shellcheck'):
            loud_skip(self, 'shellcheck is not installed')

    def test_it_should_pass_shellcheck(self):
        for script in ('setup', 'lockdown', 'start-i3'):
            with self.subTest(script=script):
                done = subprocess.run(['shellcheck', os.path.join(MACHINES, 'soak', script)],
                                      capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, done.stdout)

SECOND = 4243
OLD = 4299
SECOND_HOURLY = '0.2949'


def cancellation_of(number):
    return '/robot/server/%d/cancellation' % number


def record_for(server, listing=CHOSEN, booked='2099-01-01'):
    return {'transaction': 'B-%d' % server, 'hourly': CHOSEN_HOURLY, 'listing': listing, 'cpu': 'Intel Core i5-12500',
            'datacenter': 'FSN1-DC4', 'server_number': server, 'ip': '2a01:4f8::%d' % server, 'booked': booked,
            'earliest': booked}


class SoakRecords(Machines):
    records = {}

    @classmethod
    def seed(cls, bench):
        d = os.path.join(bench.state, 'botropolis-machines')
        os.makedirs(d, exist_ok=True)
        for name, record in cls.records.items():
            with open(os.path.join(d, name), 'w') as f:
                json.dump(record, f)

    def record_names(self):
        d = os.path.join(self.bench.state, 'botropolis-machines')
        return sorted(n for n in os.listdir(d) if n.startswith('soak') and n.endswith('.json') and n != 'soak-plan.json')

    def read_record(self, name):
        with open(os.path.join(self.bench.state, 'botropolis-machines', name)) as f:
            return json.load(f)

    def cancelled_now_of(self, number):
        return [r for r in self.bench.hetzner.sent('POST', cancellation_of(number))
                if r['form'].get('cancellation_date') == ['now']]


class WhenTwoSoakRunsStartOneAfterTheOther(SoakRecords):
    @classmethod
    def setUpClass(cls):
        cls.bench = Bench(typed=CHOSEN_HOURLY, bucket={'exit': None})
        env = cls.bench.env(**GENTLE)
        run_in_own_group([TOOL] + SOAK_PLAN, env, 60)
        cls.first = cls.start(env)
        cls.wait_for_watch(SERVER_NUMBER)
        with open(cls.bench.tty, 'w') as f:
            f.write(SECOND_HOURLY + '\n')
        run_in_own_group([TOOL] + SOAK_PLAN, env, 60)
        cls.second = cls.start(env)
        cls.wait_for_watch(SECOND)
        d = os.path.join(cls.bench.state, 'botropolis-machines')
        cls.while_both = sorted(n for n in os.listdir(d) if n.startswith('soak') and n != 'soak-plan.json')
        cls.bench.bucket.exit = '0'
        cls.outputs = [cls.finish(p) for p in (cls.first, cls.second)]

    @classmethod
    def start(cls, env):
        return subprocess.Popen([TOOL] + cls.expand(SOAK_RUN), env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, start_new_session=True)

    @classmethod
    def wait_for_watch(cls, number):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not cls.bench.bucket.sent('GET', '-%d/exit' % number):
            time.sleep(0.1)

    @classmethod
    def finish(cls, proc):
        try:
            return proc.communicate(timeout=60)
        finally:
            os.killpg(proc.pid, signal.SIGKILL) if proc.poll() is None else None

    def test_it_should_give_each_run_its_own_record(self):
        self.assertEqual(len(self.while_both), 2, self.while_both)

    def test_it_should_cancel_the_first_runs_server_once(self):
        self.assertEqual(len(self.cancelled_now_of(SERVER_NUMBER)), 1, self.outputs)

    def test_it_should_cancel_the_second_runs_server_once(self):
        self.assertEqual(len(self.cancelled_now_of(SECOND)), 1, self.outputs)

    def test_and_the_first_run_ends_it_should_say_it_cancelled_its_own_server(self):
        self.assertIn('server %d, is cancelled' % SERVER_NUMBER, self.outputs[0][0])


class WhenApplyingTheSoakOverALiveRecord(SoakRecords):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'servers': (SERVER_NUMBER,)}
    records = {'soak-%d.json' % CHOSEN: record_for(SERVER_NUMBER)}

    def test_it_should_refuse(self):
        self.assertEqual(self.done.returncode, 3, self.done.stderr)

    def test_it_should_name_the_live_server(self):
        self.assertIn('server %d' % SERVER_NUMBER, self.done.stderr)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])

    def test_it_should_leave_the_record_as_it_was(self):
        self.assertEqual(self.read_record('soak-%d.json' % CHOSEN), record_for(SERVER_NUMBER))


class WhenRunningTheSoakOverALiveRecord(SoakRecords):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'servers': (SERVER_NUMBER,)}
    records = {'soak-%d.json' % CHOSEN: record_for(SERVER_NUMBER)}

    def test_it_should_refuse(self):
        self.assertEqual(self.done.returncode, 3, self.done.stderr)

    def test_it_should_not_cancel_the_live_records_server(self):
        self.assertEqual(self.bench.hetzner.sent('DELETE', cancellation_of(SERVER_NUMBER)) +
                         self.cancelled_now_of(SERVER_NUMBER), [])


class WhenApplyingTheSoakOverARecordStillOnOrder(SoakRecords):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY
    plan_first = True
    records = {'soak-%d.json' % CHOSEN: {'transaction': 'B-unfinished', 'hourly': CHOSEN_HOURLY, 'listing': CHOSEN}}

    def test_it_should_refuse(self):
        self.assertEqual(self.done.returncode, 3, self.done.stderr)

    def test_it_should_send_no_real_order(self):
        self.assertEqual(self.bench.hetzner.orders(test=False), [])


class WhenApplyingTheSoakOverARecordWhoseServerIsGone(SoakRecords):
    argv = ['apply', 'soak'] + ROBOT_REFS
    typed = CHOSEN_HOURLY
    plan_first = True
    records = {'soak-%d.json' % CHOSEN: record_for(OLD)}

    def test_it_should_order(self):
        self.assertEqual(len(self.bench.hetzner.orders(test=False)), 1, self.done.stderr)


class WhenRunningTheSoakWithAnOldSoakJsonBeside(SoakRecords):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'servers': (OLD,)}
    records = {'soak.json': record_for(OLD, listing=3100999)}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_leave_the_old_soak_json_as_it_was(self):
        self.assertEqual(self.read_record('soak.json'), record_for(OLD, listing=3100999))

    def test_it_should_not_cancel_the_old_records_server(self):
        self.assertEqual(self.bench.hetzner.sent('DELETE', cancellation_of(OLD)) + self.cancelled_now_of(OLD), [])

    def test_it_should_cancel_its_own_server(self):
        self.assertEqual(len(self.cancelled_now_of(SERVER_NUMBER)), 1)


class WhenDestroyingTheSoakAndOnlyAnOldSoakJsonIsThere(SoakRecords):
    argv = ['destroy', 'soak'] + ROBOT_REFS
    hetzner = {'servers': (OLD,)}
    records = {'soak.json': record_for(OLD)}

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_cancel_the_server_it_names(self):
        self.assertEqual(len(self.cancelled_now_of(OLD)), 1)

    def test_it_should_remove_the_old_soak_json(self):
        self.assertEqual(self.record_names(), [])


class TwoRecords(SoakRecords):
    hetzner = {'servers': (SERVER_NUMBER, OLD)}
    records = {'soak-%d.json' % CHOSEN: record_for(SERVER_NUMBER), 'soak.json': record_for(OLD, listing=3100999)}


class WhenDestroyingTheSoakAndTwoRecordsAreThere(TwoRecords):
    argv = ['destroy', 'soak'] + ROBOT_REFS

    def test_it_should_refuse_with_exit_two(self):
        self.assertEqual(self.done.returncode, 2, self.done.stderr)

    def test_it_should_name_both_servers(self):
        self.assertEqual([str(n) in self.done.stderr for n in (SERVER_NUMBER, OLD)], [True, True], self.done.stderr)

    def test_it_should_cancel_nothing(self):
        self.assertEqual(self.cancelled_now_of(SERVER_NUMBER) + self.cancelled_now_of(OLD), [])


class WhenDestroyingTheSoakAndTwoRecordsAreThereAndAServerIsNamed(TwoRecords):
    argv = ['destroy', 'soak', '--server', str(SERVER_NUMBER)] + ROBOT_REFS

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_cancel_only_that_server(self):
        self.assertEqual((len(self.cancelled_now_of(SERVER_NUMBER)), len(self.cancelled_now_of(OLD))), (1, 0))

    def test_it_should_leave_the_other_record(self):
        self.assertEqual(self.record_names(), ['soak.json'])


class WhenDestroyingTheSoakAndTheNamedServerHasNoRecord(TwoRecords):
    argv = ['destroy', 'soak', '--server', '9999'] + ROBOT_REFS

    def test_it_should_refuse_naming_it(self):
        self.assertIn('9999', self.done.stderr)

    def test_it_should_cancel_nothing(self):
        self.assertEqual(self.cancelled_now_of(SERVER_NUMBER) + self.cancelled_now_of(OLD), [])


if __name__ == '__main__':
    unittest.main()
