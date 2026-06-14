"""Tests for the worker assignment problem (Exercise 5)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from designacao import TIMES, solve


class TestDesignacao(unittest.TestCase):

    def setUp(self) -> None:
        self.sol = solve()

    def test_each_worker_gets_one_task(self) -> None:
        """Every worker is assigned exactly one task (valid index, no duplicates)."""
        assignment = self.sol["assignment"]
        self.assertEqual(len(assignment), 6)
        for task in assignment:
            self.assertIn(task, range(6), msg=f"Invalid task index {task}")

    def test_each_task_assigned_once(self) -> None:
        """Every task is covered by exactly one worker (no duplicates)."""
        assignment = self.sol["assignment"]
        self.assertEqual(
            len(set(assignment)), 6,
            msg="Some tasks appear more than once or are unassigned",
        )

    def test_times_match_cost_matrix(self) -> None:
        """Each reported assignment time matches the TIMES matrix entry."""
        for i, (task_idx, t) in enumerate(
            zip(self.sol["assignment"], self.sol["times"])
        ):
            expected = float(TIMES[i, task_idx])
            self.assertAlmostEqual(t, expected, places=4)

    def test_total_matches_linear_sum_assignment(self) -> None:
        """milp total time equals the value from linear_sum_assignment."""
        self.assertAlmostEqual(
            self.sol["total_time"],
            self.sol["verify_total"],
            places=2,
            msg="milp total diverges from linear_sum_assignment reference",
        )


if __name__ == "__main__":
    unittest.main()
