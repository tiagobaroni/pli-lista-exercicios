"""End-to-end tests: B&B optimal value must match scipy.optimize.milp."""

import unittest

from bb.model import build_exercicio_1, build_exercicio_2, build_exercicio_4
from bb.relaxation import verify_with_milp
from bb.solver import BranchAndBoundSolver

_TOL = 1e-4


class TestEndToEnd(unittest.TestCase):

    def _run(self, builder):
        model = builder()
        solver = BranchAndBoundSolver(model=model, strategy="dfs", max_nodes=None)
        nodes = solver.solve()
        incumbent = next((n for n in nodes if n.is_incumbent), None)
        self.assertIsNotNone(incumbent, f"No incumbent found for {model.name}")
        return incumbent.Z, verify_with_milp(model)

    def test_exercicio_1_matches_milp(self):
        bb_z, milp_z = self._run(build_exercicio_1)
        self.assertAlmostEqual(bb_z, milp_z, delta=_TOL,
            msg=f"Ex1: B&B={bb_z}, milp={milp_z}")

    def test_exercicio_2_matches_milp(self):
        bb_z, milp_z = self._run(build_exercicio_2)
        self.assertAlmostEqual(bb_z, milp_z, delta=_TOL,
            msg=f"Ex2: B&B={bb_z}, milp={milp_z}")

    def test_exercicio_4_matches_milp(self):
        bb_z, milp_z = self._run(build_exercicio_4)
        self.assertAlmostEqual(bb_z, milp_z, delta=_TOL,
            msg=f"Ex4: B&B={bb_z}, milp={milp_z}")

    def test_exercicio_1_bfs_matches_dfs(self):
        model = build_exercicio_1()
        dfs_solver = BranchAndBoundSolver(model=model, strategy="dfs")
        bfs_solver = BranchAndBoundSolver(model=model, strategy="bfs")
        dfs_nodes = dfs_solver.solve()
        bfs_nodes = bfs_solver.solve()
        dfs_z = next(n.Z for n in dfs_nodes if n.is_incumbent)
        bfs_z = next(n.Z for n in bfs_nodes if n.is_incumbent)
        self.assertAlmostEqual(dfs_z, bfs_z, delta=_TOL)


if __name__ == "__main__":
    unittest.main()
