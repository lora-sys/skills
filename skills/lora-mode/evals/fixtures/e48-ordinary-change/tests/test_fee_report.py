import unittest

from fee_report import csv_header


class FeeReportTests(unittest.TestCase):
    def test_csv_header(self):
        self.assertEqual(csv_header(), "Date,Description,Fee")


if __name__ == "__main__":
    unittest.main()
