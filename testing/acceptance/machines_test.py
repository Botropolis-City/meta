import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'helpers'))
from hetzner import CHOSEN, CHOSEN_HOURLY, IPV6_NET, SECRET, SERVER_NUMBER, Bench, basic, listing  # noqa: E402
from stubs import run_in_own_group  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MACHINES = os.path.join(ROOT, 'testing', 'machines')
TOOL = os.path.join(MACHINES, 'machines')
ROBOT_REFS = ['--robot-user-ref', 'op:Test/robot/user', '--robot-password-ref', 'op:Test/robot/password']
HCLOUD_REFS = ['--hcloud-token-ref', 'op:Test/hcloud/token']
CANCELLATION = '/robot/server/%d/cancellation' % SERVER_NUMBER
ORDER = '/robot/order/server_market/transaction'
SOAK_PLAN = ['plan', 'soak'] + ROBOT_REFS


def loud_skip(case, reason):
    sys.stderr.write('\n  SKIPPED %s: %s\n' % (case.id(), reason))
    case.skipTest(reason)


class Machines(unittest.TestCase):
    argv = []
    typed = ''
    hetzner = {}
    stub_env = {}
    plan_first = False

    @classmethod
    def setUpClass(cls):
        cls.bench = Bench(typed=cls.typed, **cls.hetzner)
        if cls.plan_first:
            cls.planned = run_in_own_group([TOOL] + SOAK_PLAN, cls.bench.env(), 60)
            cls.after_plan(cls.bench.hetzner)
        cls.done = run_in_own_group([TOOL] + cls.expand(cls.argv), cls.bench.env(**cls.stub_env), 60)

    @classmethod
    def after_plan(cls, hetzner):
        pass

    @classmethod
    def expand(cls, argv):
        b = cls.bench
        names = {'{build}': b.build, '{stager}': b.stager, '{corpus}': b.corpus, '{script}': b.script, '{out}': b.out,
                 '{history}': b.history, '{real-history}': b.real_history}
        return [names.get(a, a) for a in argv]

    @classmethod
    def tearDownClass(cls):
        cls.bench.close()

    def ssh_commands(self):
        return [' '.join(argv) for argv in self.bench.calls('ssh')]


SOAK_RUN = ['run', 'soak'] + ROBOT_REFS + ['--build', '{build}', '--stager', '{stager}', '--corpus', '{corpus}',
                                           '--history', '{history}', '--out', '{out}']
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

    def test_it_should_order_without_the_paid_ipv4_addon(self):
        self.assertNotIn('addon[]', self.bench.hetzner.orders(test=True)[0]['form'])


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
        self.assertEqual(self.bench.hetzner.sent('POST', CANCELLATION), [])

    def test_it_should_say_how_to_destroy_it(self):
        self.assertIn('destroy', self.done.stdout)


class WhenDestroyingTheSoakWithNothingOrdered(Machines):
    argv = ['destroy', 'soak'] + ROBOT_REFS

    def test_it_should_exit_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr)

    def test_it_should_cancel_nothing(self):
        self.assertEqual(self.bench.hetzner.sent('POST', CANCELLATION), [])


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

    def test_it_should_cancel_the_server_now(self):
        self.assertEqual([r['form'].get('cancellation_date') for r in self.bench.hetzner.sent('POST', CANCELLATION)], [['now']])


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

    def test_it_should_fetch_the_report(self):
        self.assertTrue([argv for argv in self.bench.calls('scp') if argv[-1] == self.bench.out], self.bench.calls('scp'))

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.bench.hetzner.sent('POST', CANCELLATION)), 1)

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
    stub_env = {'STUB_FAIL': 'ssh:perf-soak'}

    def test_it_should_exit_nonzero(self):
        self.assertNotEqual(self.done.returncode, 0)

    def test_it_should_still_fetch_the_report(self):
        self.assertTrue([argv for argv in self.bench.calls('scp') if argv[-1] == self.bench.out], self.bench.calls('scp'))

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.bench.hetzner.sent('POST', CANCELLATION)), 1)


class WhenRunningTheSoakAndTheSetUpFails(Machines):
    argv = SOAK_RUN
    typed = CHOSEN_HOURLY
    plan_first = True
    hetzner = {'server_ip': '192.0.2.44'}
    stub_env = {'STUB_FAIL': 'ssh:setup'}

    def test_it_should_not_start_the_soak(self):
        self.assertFalse([c for c in self.ssh_commands() if 'perf-soak' in c])

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.bench.hetzner.sent('POST', CANCELLATION)), 1)


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
        cls.bench = Bench(typed=cls.typed, **cls.hetzner)
        run_in_own_group([TOOL] + SOAK_PLAN, cls.bench.env(), 60)
        proc = subprocess.Popen([TOOL] + cls.expand(cls.argv), env=cls.bench.env(STUB_HANG='ssh:perf-soak'),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not [c for c in cls.bench.calls('ssh') if 'perf-soak' in ' '.join(c)]:
            time.sleep(0.1)
        proc.send_signal(signal.SIGINT)
        try:
            proc.communicate(timeout=30)
        finally:
            os.killpg(proc.pid, signal.SIGKILL) if proc.poll() is None else None

    def test_it_should_cancel_the_server(self):
        self.assertEqual(len(self.bench.hetzner.sent('POST', CANCELLATION)), 1)


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
        done = subprocess.run(['shellcheck', os.path.join(MACHINES, 'soak', 'setup')], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout)


if __name__ == '__main__':
    unittest.main()
