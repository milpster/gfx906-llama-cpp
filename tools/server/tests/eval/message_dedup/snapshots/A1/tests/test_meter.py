import unittest

from src import meter


class WithinQuotaTests(unittest.TestCase):
    def test_exactly_used_up_is_within_quota(self):
        self.assertTrue(meter.within_quota(10, 10))

    def test_below_quota(self):
        self.assertTrue(meter.within_quota(3, 10))

    def test_over_quota(self):
        self.assertFalse(meter.within_quota(11, 10))

    def test_negative_quota_is_rejected(self):
        with self.assertRaises(ValueError):
            meter.within_quota(1, -1)
