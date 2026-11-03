import unittest

from reservation import ReservationBook


class ReservationTests(unittest.TestCase):
    def test_capacity_confirm_and_cancel(self):
        book = ReservationBook(capacity=1)
        self.assertTrue(book.create("r1", "alice"))
        self.assertFalse(book.create("r2", "bob"))
        self.assertTrue(book.cancel("r1", "alice"))
        self.assertTrue(book.create("r2", "bob"))
        self.assertTrue(book.confirm("r2", "bob"))
        self.assertFalse(book.cancel("r2", "bob"))


if __name__ == "__main__":
    unittest.main()
