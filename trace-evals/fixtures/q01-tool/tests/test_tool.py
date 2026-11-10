import unittest
from parser import parse_line


class TestParse(unittest.TestCase):
    def test_plain_decimal(self):
        self.assertEqual(parse_line("12.50"), 12.50)


if __name__ == "__main__":
    unittest.main()
