"""Tests for branching variable selection in the B&B solver."""

import unittest
import numpy as np

from bb.solver import _select_branch_variable
from bb.model import MILPModel


class TestSelectBranchVariable(unittest.TestCase):

    def _make_model(self, n_vars: int, integers: list[int]) -> MILPModel:
        return MILPModel(
            c=np.zeros(n_vars),
            A_ub=np.zeros((1, n_vars)),
            b_ub=np.zeros(1),
            bounds=[(0.0, None)] * n_vars,
            integers=integers,
            sense="max",
            var_names=[f"x{i+1}" for i in range(n_vars)],
            name="test",
        )

    def test_selects_most_fractional(self):
        # x1=0.2 (frac=0.2), x2=0.7 (frac=0.3) → x2 is most fractional
        x = np.array([0.2, 0.7])
        model = self._make_model(2, [0, 1])
        self.assertEqual(_select_branch_variable(x, model), 1)

    def test_tiebreak_by_smallest_index(self):
        # x1=0.5, x2=0.5 → both frac=0.5, x1 wins (index 0)
        x = np.array([0.5, 0.5])
        model = self._make_model(2, [0, 1])
        self.assertEqual(_select_branch_variable(x, model), 0)

    def test_skips_continuous_variables(self):
        # x1=0.9 (continuous), x2=0.5 (integer) → x2 must be chosen
        x = np.array([0.9, 0.5])
        model = self._make_model(2, [1])  # only x2 is integer
        self.assertEqual(_select_branch_variable(x, model), 1)

    def test_symmetry_frac_above_half(self):
        # x1=0.8 → distance to nearest int = min(0.8, 0.2) = 0.2
        # x2=0.4 → distance = min(0.4, 0.6) = 0.4  → x2 wins
        x = np.array([0.8, 0.4])
        model = self._make_model(2, [0, 1])
        self.assertEqual(_select_branch_variable(x, model), 1)

    def test_exact_integer_not_chosen(self):
        # x1=1.0 (exact), x2=0.5 (fractional) → x2
        x = np.array([1.0, 0.5])
        model = self._make_model(2, [0, 1])
        self.assertEqual(_select_branch_variable(x, model), 1)

    def test_returns_minus_one_when_all_integers_are_exact(self):
        # all integer vars are exact → no fractional var → return -1
        x = np.array([2.0, 3.0])
        model = self._make_model(2, [0, 1])
        self.assertEqual(_select_branch_variable(x, model), -1)


if __name__ == "__main__":
    unittest.main()
