import unittest

from ledgerkit import money


class ParseCentsTests(unittest.TestCase):
    def test_plain_amount(self):
        self.assertEqual(money.parse_cents("12.30"), 1230)

    def test_single_decimal_digit(self):
        self.assertEqual(money.parse_cents("12.3"), 1230)

    def test_negative_amount(self):
        self.assertEqual(money.parse_cents("-0.05"), -5)


class FormatCentsTests(unittest.TestCase):
    def test_negative_amount(self):
        self.assertEqual(money.format_cents(-5), "-0.05")

    def test_round_trip(self):
        self.assertEqual(money.format_cents(money.parse_cents("7.40")), "7.40")


class SplitEvenlyTests(unittest.TestCase):
    def test_remainder_goes_to_first_shares(self):
        self.assertEqual(money.split_evenly(100, 3), [34, 33, 33])

    def test_even_split(self):
        self.assertEqual(money.split_evenly(90, 3), [30, 30, 30])

    def test_parts_must_be_positive(self):
        with self.assertRaises(ValueError):
            money.split_evenly(10, 0)
