import unittest

from app import add_mod


class TestAddMod(unittest.TestCase):
    def test_add_mod_basic(self) -> None:
        self.assertEqual(add_mod(2, 3, 97), 5)
        self.assertEqual(add_mod(96, 2, 97), 1)

    def test_add_mod_zero(self) -> None:
        self.assertEqual(add_mod(0, 0, 97), 0)
        self.assertEqual(add_mod(0, 5, 97), 5)


if __name__ == "__main__":
    unittest.main()

