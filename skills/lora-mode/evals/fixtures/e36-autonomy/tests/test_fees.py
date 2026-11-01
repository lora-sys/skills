import unittest

from fees import parse_amount, total_amounts


class FeeTests(unittest.TestCase):
    def test_parse_plain_amount(self):
        self.assertEqual(parse_amount("12.50"), 12.50)

    def test_parse_dollar_amount(self):
        self.assertEqual(parse_amount("$4.25"), 4.25)

    def test_total_amounts(self):
        self.assertEqual(total_amounts(["12.50", "$4.25"]), 16.75)


if __name__ == "__main__":
    unittest.main()
