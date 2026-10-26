import unittest

from auction import choose, xe_igpu

XE = ['Intel Core i5-12500', 'Intel Core i5-13500', 'Intel Core i9-13900', 'Intel Core i9-12900K',
      'Intel Core i7-14700', 'Intel Core Ultra 7 265', 'Intel Core Ultra 5 245K']
NOT_XE = ['Intel Core i7-6700', 'Intel Core i7-7700', 'Intel Core i7-8700', 'Intel Core i9-9900K',
          'Intel Core i5-12400F', 'Intel Core i9-13900KF', 'Intel Core Ultra 7 265KF',
          'Intel Xeon E3-1275v5', 'Intel Xeon E3-1275V6', 'Intel XEON E-2176G', 'Intel XEON E-2276G',
          'Intel Xeon E3-1270V3', 'Intel Xeon E5-1650V3', 'Intel Xeon W-2145', 'Intel Xeon W-2295',
          'Intel Xeon Gold 5412U', 'AMD Ryzen 7 7700', 'AMD Ryzen 7 PRO 8700GE', 'AMD EPYC 7401P', '']


def listing(id, cpu, hourly, setup='0.0000'):
    return {'id': id, 'cpu': cpu, 'price_hourly': hourly, 'price_setup': setup, 'price': '100.0000',
            'datacenter': 'FSN1-DC1'}


class WhenDecidingWhetherACPUHasAnXeClassIntelGPU(unittest.TestCase):
    def test_it_should_accept_every_core_of_12th_gen_and_later_with_graphics(self):
        for cpu in XE:
            with self.subTest(cpu=cpu):
                self.assertTrue(xe_igpu(cpu))

    def test_it_should_refuse_older_cores_f_parts_xeons_and_amd(self):
        for cpu in NOT_XE:
            with self.subTest(cpu=cpu):
                self.assertFalse(xe_igpu(cpu))


class WhenChoosingTheSoakBox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chosen, cls.why = choose([
            listing(1, 'AMD Ryzen 7 7700', '0.1000'),
            listing(2, 'Intel Core i7-6700', '0.1100'),
            listing(3, 'Intel Core i5-13500', '0.1200', setup='39.0000'),
            listing(4, 'Intel Core i5-12500', None),
            listing(5, 'Intel Core i9-13900', '0.2949'),
            listing(6, 'Intel Core i5-12500', '0.1763'),
            listing(7, 'Intel Core i5-12500', '0.1800'),
        ])

    def test_it_should_take_the_cheapest_hourly_xe_listing_with_no_setup_fee(self):
        self.assertEqual(self.chosen['id'], 6)


class WhenChoosingTheSoakBoxAndNothingQualifies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chosen, cls.why = choose([
            listing(1, 'AMD Ryzen 7 7700', '0.1000'),
            listing(3, 'Intel Core i5-13500', '0.1200', setup='39.0000'),
            listing(4, 'Intel Core i5-12500', None),
        ])

    def test_it_should_choose_nothing(self):
        self.assertIsNone(self.chosen)

    def test_it_should_say_how_many_had_a_setup_fee(self):
        self.assertIn('1 with a setup fee', self.why)

    def test_it_should_say_how_many_had_no_hourly_price(self):
        self.assertIn('1 with no hourly price', self.why)


if __name__ == '__main__':
    unittest.main()
