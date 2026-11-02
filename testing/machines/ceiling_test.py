import importlib.machinery
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_loader = importlib.machinery.SourceFileLoader('machines_ceiling', os.path.join(HERE, 'machines'))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
machines = importlib.util.module_from_spec(_spec)
_loader.exec_module(machines)

CYCLE_S = 5 * 180 + 600
SOAK_S = 28800 + 600


class WhenComputingTheSoaksHours(unittest.TestCase):
    def test_and_the_flags_are_the_defaults_it_should_count_the_cycle_and_the_soak(self):
        self.assertAlmostEqual(machines.soak_hours(''), (CYCLE_S + SOAK_S) / 3600)

    def test_and_the_soak_is_given_its_seconds_it_should_count_those(self):
        self.assertAlmostEqual(machines.soak_hours('--seconds 3600'), (CYCLE_S + 3600 + 600) / 3600)

    def test_and_the_cycle_is_turned_off_it_should_count_the_soak_alone(self):
        self.assertAlmostEqual(machines.soak_hours('--no-cycle'), SOAK_S / 3600)


class WhenChoosingTheCeiling(unittest.TestCase):
    def test_and_none_is_given_it_should_be_the_cycle_and_the_soak_and_the_margin(self):
        self.assertAlmostEqual(machines.ceiling_hours(None, ''), (CYCLE_S + SOAK_S) / 3600 + machines.CEILING_MARGIN_H)

    def test_and_one_is_given_it_should_keep_it(self):
        self.assertEqual(machines.ceiling_hours(12.5, ''), 12.5)

    def test_it_should_leave_the_set_up_two_hours(self):
        self.assertEqual(machines.CEILING_MARGIN_H, 2.0)


if __name__ == '__main__':
    unittest.main()
