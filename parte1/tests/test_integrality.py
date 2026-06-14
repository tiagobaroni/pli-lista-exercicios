"""Tests for the integrality check used in the B&B solver."""

import unittest
import numpy as np

from bb.solver import _is_integer_feasible, _INTEG_TOL


class TestIntegerFeasible(unittest.TestCase):

    def _make_model_integers(self, indices):
        """Return a dummy object with only the integers attribute set."""
        class _M:
            integers = indices
        return _M()

    def test_all_exact_integers_are_feasible(self):
        x = np.array([0.0, 1.0, 3.0, 2.0])
        model = self._make_model_integers([0, 1, 2, 3])
        self.assertTrue(_is_integer_feasible(x, model))

    def test_fractional_integer_variable_is_infeasible(self):
        x = np.array([0.0, 1.5, 3.0])
        model = self._make_model_integers([0, 1, 2])
        self.assertFalse(_is_integer_feasible(x, model))

    def test_within_tolerance_is_feasible(self):
        x = np.array([2.0 + _INTEG_TOL * 0.5])
        model = self._make_model_integers([0])
        self.assertTrue(_is_integer_feasible(x, model))

    def test_just_outside_tolerance_is_infeasible(self):
        x = np.array([2.0 + _INTEG_TOL * 2])
        model = self._make_model_integers([0])
        self.assertFalse(_is_integer_feasible(x, model))

    def test_continuous_variable_ignored(self):
        # x[1]=1.7 is continuous, so the solution is still integer-feasible
        x = np.array([2.0, 1.7, 3.0])
        model = self._make_model_integers([0, 2])  # index 1 is continuous
        self.assertTrue(_is_integer_feasible(x, model))

    def test_all_variables_continuous(self):
        x = np.array([1.3, 2.7])
        model = self._make_model_integers([])
        self.assertTrue(_is_integer_feasible(x, model))


if __name__ == "__main__":
    unittest.main()
