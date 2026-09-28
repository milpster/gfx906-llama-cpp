import unittest

from shipping import rates


class BillableWeightTests(unittest.TestCase):
    def test_exact_kilograms_are_not_rounded_up(self):
        self.assertEqual(rates.billable_weight(2.0), 2)

    def test_fractions_round_up(self):
        self.assertEqual(rates.billable_weight(2.1), 3)


class BaseRateTests(unittest.TestCase):
    def test_first_kilogram_is_free(self):
        self.assertEqual(rates.base_rate(0.4), 450)


class QuoteTests(unittest.TestCase):
    def test_local_quote(self):
        self.assertEqual(rates.quote(1.5, "local"), 570)

    def test_regional_quote_rounds_half_up(self):
        # base 810 cents * 135 % = 1093.5 -> 1094
        self.assertEqual(rates.quote(3.5, "regional"), 1094)

    def test_remote_zone_is_priced_at_245_percent(self):
        self.assertEqual(rates.zone_multiplier("remote"), 245)
        self.assertEqual(rates.quote(1.0, "remote"), 1103)


if __name__ == "__main__":
    unittest.main()
