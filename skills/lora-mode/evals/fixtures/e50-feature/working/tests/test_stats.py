import unittest

from stats import main


class StatsTests(unittest.TestCase):
    def test_summary_reports_nonempty_rows(self):
        self.assertEqual(main(["a", "", "b"], summary=True), "Rows: 2")


if __name__ == "__main__":
    unittest.main()
