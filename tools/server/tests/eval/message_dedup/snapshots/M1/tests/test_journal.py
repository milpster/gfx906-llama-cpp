import unittest

from ledgerkit import journal


class PostEntryTests(unittest.TestCase):
    def setUp(self):
        self.journal = journal.Journal()

    def test_balanced_entry_is_posted(self):
        n = journal.post_entry(self.journal, "sale", [("1000", 500, 0), ("4000", 0, 500)])
        self.assertEqual(n, 1)

    def test_unbalanced_entry_is_rejected(self):
        with self.assertRaises(ValueError):
            journal.post_entry(self.journal, "sale", [("1000", 500, 0), ("4000", 0, 400)])

    def test_single_line_entry_is_rejected(self):
        with self.assertRaises(ValueError):
            journal.post_entry(self.journal, "odd", [("1000", 500, 500)])

    def test_lines_are_flattened(self):
        journal.post_entry(self.journal, "rent", [("6100", 900, 0), ("1000", 0, 900)])
        journal.post_entry(self.journal, "fee", [("6200", 30, 0), ("1000", 0, 30)])
        self.assertEqual(len(self.journal.lines()), 4)

    def test_memo_is_kept(self):
        journal.post_entry(self.journal, "rent", [("6100", 900, 0), ("1000", 0, 900)])
        self.assertEqual(self.journal.entries[0]["memo"], "rent")
