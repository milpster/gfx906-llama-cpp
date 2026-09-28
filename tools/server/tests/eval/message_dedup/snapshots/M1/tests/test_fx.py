import unittest

from ledgerkit import fx


class ConvertTests(unittest.TestCase):
    def test_same_currency_is_identity(self):
        self.assertEqual(fx.convert(1234, "EUR", "EUR"), 1234)

    def test_whole_result(self):
        self.assertEqual(fx.convert(1000, "EUR", "USD"), 1085)

    def test_rounds_half_away_from_zero(self):
        self.assertEqual(fx.convert(7, "EUR", "GBP"), 6)

    def test_negative_amounts_round_symmetrically(self):
        self.assertEqual(fx.convert(-7, "EUR", "GBP"), -6)

    def test_missing_rate_is_an_error(self):
        with self.assertRaises(ValueError):
            fx.convert(1, "CHF", "USD")
