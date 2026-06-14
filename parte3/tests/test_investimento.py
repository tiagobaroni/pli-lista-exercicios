"""Tests for the investment selection problem (Exercise 6)."""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from investimento import BUDGET, MAX_PROJECTS, solve


class TestInvestimento(unittest.TestCase):

    def setUp(self) -> None:
        self.sol = solve()
        self.y = np.array(self.sol["y"])

    def test_constraint_a(self) -> None:
        """y_2 <= y_1 (Proj 2 complementary to Proj 1)."""
        self.assertLessEqual(int(self.y[1]), int(self.y[0]))

    def test_constraint_b(self) -> None:
        """y_3 + y_4 <= 1 (Projs 3 and 4 mutually exclusive)."""
        self.assertLessEqual(int(self.y[2] + self.y[3]), 1)

    def test_constraint_c(self) -> None:
        """y_5 <= y_4 (Proj 5 complementary to Proj 4)."""
        self.assertLessEqual(int(self.y[4]), int(self.y[3]))

    def test_constraint_d(self) -> None:
        """y_6 + y_7 <= 1 (Projs 6 and 7 mutually exclusive)."""
        self.assertLessEqual(int(self.y[5] + self.y[6]), 1)

    def test_constraint_e(self) -> None:
        """y_8 + y_9 + y_10 <= 1 (Projs 8, 9, 10 mutually exclusive)."""
        self.assertLessEqual(int(self.y[7] + self.y[8] + self.y[9]), 1)

    def test_constraint_f1(self) -> None:
        """y_8+y_9+y_10 <= y_6+y_7 (production requires supply)."""
        self.assertLessEqual(
            int(self.y[7] + self.y[8] + self.y[9]),
            int(self.y[5] + self.y[6]),
        )

    def test_constraint_f2(self) -> None:
        """y_8+y_9+y_10 <= y_3+y_4 (production requires storage)."""
        self.assertLessEqual(
            int(self.y[7] + self.y[8] + self.y[9]),
            int(self.y[2] + self.y[3]),
        )

    def test_budget_respected(self) -> None:
        """Total investment does not exceed the budget."""
        self.assertLessEqual(self.sol["total_investment"], BUDGET + 1e-4)

    def test_manager_limit_respected(self) -> None:
        """Number of selected projects does not exceed the manager limit."""
        self.assertLessEqual(self.sol["n_selected"], MAX_PROJECTS)

    def test_vp_positive(self) -> None:
        """At least one project is selected and total VP is positive."""
        self.assertGreater(self.sol["total_vp"], 0.0)


if __name__ == "__main__":
    unittest.main()
