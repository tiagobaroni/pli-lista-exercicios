"""Tests for the transportation problem (Exercise 4)."""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from transporte import DEMAND, SUPPLY, solve


class TestTransporte(unittest.TestCase):

    def setUp(self) -> None:
        self.sol = solve()

    def test_supply_constraints(self) -> None:
        """Each centre ships exactly its supply (real + dummy destinations)."""
        alloc = self.sol["allocation"]
        dummy = self.sol["dummy_allocation"]
        for i, cap in enumerate(SUPPLY):
            total = float(alloc[i].sum() + dummy[i])
            self.assertAlmostEqual(
                total, cap, places=4,
                msg=f"C{i+1} supply not met: sent {total:.4f}, capacity {cap}",
            )

    def test_demand_constraints(self) -> None:
        """Each real warehouse receives exactly its demand."""
        alloc = self.sol["allocation"]
        for j, dem in enumerate(DEMAND):
            received = float(alloc[:, j].sum())
            self.assertAlmostEqual(
                received, dem, places=4,
                msg=f"W{j+1} demand not met: received {received:.4f}, demand {dem}",
            )

    def test_all_allocations_nonnegative(self) -> None:
        """No allocation is negative (allows tiny float noise)."""
        self.assertTrue(
            np.all(self.sol["allocation"] >= -1e-9),
            "Negative allocation in real warehouses",
        )
        self.assertTrue(
            np.all(self.sol["dummy_allocation"] >= -1e-9),
            "Negative allocation to dummy destination",
        )

    def test_total_cost_nonnegative(self) -> None:
        """Total transportation cost is non-negative."""
        self.assertGreaterEqual(self.sol["total_cost"], 0.0)


if __name__ == "__main__":
    unittest.main()
