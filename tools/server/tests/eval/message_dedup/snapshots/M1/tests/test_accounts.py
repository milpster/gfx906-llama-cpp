import unittest

from ledgerkit import accounts


class BalanceTests(unittest.TestCase):
    def setUp(self):
        self.cash = accounts.Account("1000", "Cash", "asset")
        self.sales = accounts.Account("4000", "Sales", "income")
        self.lines = [("1000", 5000, 0), ("4000", 0, 5000), ("1000", 0, 1200), ("6100", 1200, 0)]

    def test_asset_balance_is_debit_normal(self):
        self.assertEqual(accounts.balance_of(self.lines, self.cash), 3800)

    def test_income_balance_is_credit_normal(self):
        self.assertEqual(accounts.balance_of(self.lines, self.sales), 5000)

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            accounts.Account("9000", "Misc", "misc")

    def test_expense_is_debit_normal(self):
        self.assertEqual(accounts.normal_sign("expense"), 1)
