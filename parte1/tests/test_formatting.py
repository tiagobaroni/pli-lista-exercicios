"""Tests for Brazilian-locale number formatting in formatting.py."""

import unittest

from bb.formatting import format_number


class TestFormatNumber(unittest.TestCase):

    # Objective values (is_objective=True) - always 2 decimal places
    def test_objective_integer_shows_two_decimals(self):
        self.assertEqual(format_number(19.0, is_objective=True), "19,00")

    def test_objective_fractional_shows_two_decimals(self):
        self.assertEqual(format_number(19.25, is_objective=True), "19,25")

    def test_objective_uses_comma_as_decimal_separator(self):
        self.assertNotIn(".", format_number(3.14, is_objective=True))
        self.assertIn(",", format_number(3.14, is_objective=True))

    # Variable values (is_objective=False)
    def test_exact_integer_shows_no_decimal(self):
        self.assertEqual(format_number(2.0), "2")
        self.assertEqual(format_number(0.0), "0")

    def test_fractional_uses_comma_separator(self):
        result = format_number(1.5)
        self.assertIn(",", result)
        self.assertNotIn(".", result)

    def test_fractional_strips_trailing_zeros(self):
        # 0.5000 → "0,5" not "0,5000"
        self.assertEqual(format_number(0.5), "0,5")

    def test_four_decimal_places_max(self):
        # 1/3 ≈ 0.3333... → "0,3333"
        self.assertEqual(format_number(1 / 3), "0,3333")

    def test_rounding_at_fourth_decimal(self):
        # 2/3 ≈ 0.6666... → "0,6667" (rounds up)
        self.assertEqual(format_number(2 / 3), "0,6667")

    def test_value_near_integer_within_tolerance_shows_integer(self):
        # 2.0 + 5e-10 is close enough to 2 → "2"
        self.assertEqual(format_number(2.0 + 5e-10), "2")


if __name__ == "__main__":
    unittest.main()
