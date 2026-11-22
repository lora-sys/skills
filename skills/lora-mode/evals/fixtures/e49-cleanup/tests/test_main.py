import unittest

from main import main


class MainTests(unittest.TestCase):
    def test_loads_configured_plugins(self):
        self.assertEqual(main(), ["legacy report"])


if __name__ == "__main__":
    unittest.main()
