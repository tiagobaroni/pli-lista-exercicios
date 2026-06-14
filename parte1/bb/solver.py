"""Branch-and-Bound solver for Mixed-Integer Linear Programs."""

from __future__ import annotations

import math
from collections import deque
from typing import Literal

import numpy as np

from bb.model import BBNode, MILPModel
from bb.relaxation import solve_relaxation

_INTEG_TOL: float = 1e-6
_BOUND_TOL: float = 1e-6


def _is_integer_feasible(x: np.ndarray, model: MILPModel) -> bool:
    """Return True if all integer-constrained variables have integer values.

    Parameters
    ----------
    x:
        Solution vector from the LP relaxation.
    model:
        MILP model supplying the list of integer variable indices.
    """
    for j in model.integers:
        if abs(x[j] - round(x[j])) >= _INTEG_TOL:
            return False
    return True


def _select_branch_variable(x: np.ndarray, model: MILPModel) -> int:
    """Return the index of the most-fractional integer variable.

    Fractionality is measured as min(frac, 1-frac) where frac = v - floor(v).
    Ties are broken by the smallest index.
    Returns -1 if all integer variables are already integer-valued.

    Parameters
    ----------
    x:
        Solution vector from the LP relaxation.
    model:
        MILP model supplying the list of integer variable indices.
    """
    best_idx = -1
    best_frac = -1.0
    for j in model.integers:
        frac = x[j] - math.floor(x[j])
        dist = min(frac, 1.0 - frac)
        if dist < _INTEG_TOL:
            continue
        if dist > best_frac:
            best_frac = dist
            best_idx = j
    return best_idx


def _effective_branch_constraints(
    node_bounds: list[tuple[float, float | None]],
    original_bounds: list[tuple[float, float | None]],
    var_names: list[str],
) -> list[str]:
    """Build the list of bound constraints that differ from the original.

    Only the tightest bound per variable (versus the original) is reported.

    Parameters
    ----------
    node_bounds:
        Bounds active at this node.
    original_bounds:
        Bounds from the root model.
    var_names:
        Variable names for formatting.
    """
    parts: list[str] = []
    for j, (nb, ob) in enumerate(zip(node_bounds, original_bounds)):
        n_lb, n_ub = nb
        o_lb, o_ub = ob
        if n_ub != o_ub and n_ub is not None:
            parts.append(f"{var_names[j]} <= {int(n_ub) if n_ub == int(n_ub) else n_ub}")
        if n_lb != o_lb:
            parts.append(f"{var_names[j]} >= {int(n_lb) if n_lb == int(n_lb) else n_lb}")
    return parts


class BranchAndBoundSolver:
    """Branch-and-Bound solver for a MILPModel.

    Parameters
    ----------
    model:
        The problem to solve.
    strategy:
        Search strategy: 'dfs' (depth-first, LIFO stack) or 'bfs' (breadth-first, FIFO queue).
    max_nodes:
        Maximum number of nodes to process before stopping. None means no limit.
    """

    def __init__(
        self,
        model: MILPModel,
        strategy: Literal["dfs", "bfs"] = "dfs",
        max_nodes: int | None = None,
    ) -> None:
        self.model = model
        self.strategy = strategy
        self.max_nodes = max_nodes
        self.nodes: list[BBNode] = []
        self.tree_complete: bool = False
        self._next_id: int = 0
        self._incumbent_z: float = -math.inf if model.sense == "max" else math.inf

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def solve(self) -> list[BBNode]:
        """Run the B&B algorithm and return all processed nodes.

        Returns
        -------
        list[BBNode]
            All nodes in creation order, with final statuses set.
        """
        queue: deque[BBNode] = deque()
        root = BBNode(
            id=self._next_id,
            parent_id=None,
            bounds=list(self.model.bounds),
            branch_constraints=[],
        )
        self._next_id += 1
        queue.append(root)

        nodes_solved = 0

        while queue:
            if self.max_nodes is not None and nodes_solved >= self.max_nodes:
                break

            node = queue.pop() if self.strategy == "dfs" else queue.popleft()
            self._process_node(node, queue)
            self.nodes.append(node)
            nodes_solved += 1

        self.tree_complete = len(queue) == 0
        self._mark_incumbent()
        return self.nodes

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_node(self, node: BBNode, queue: deque[BBNode]) -> None:
        """Solve the relaxation at *node* and apply pruning or branching."""
        result = solve_relaxation(self.model, node.bounds)

        if not result.feasible:
            node.status = "Solução Infactível"
            return

        z = result.Z
        x = result.x

        # Prune by bound
        if self.model.sense == "max":
            dominated = z <= self._incumbent_z + _BOUND_TOL
        else:
            dominated = z >= self._incumbent_z - _BOUND_TOL

        if dominated:
            node.Z = z
            node.x = x
            node.status = "Inferior a melhor já obtida"
            return

        # Integer feasibility
        if _is_integer_feasible(x, self.model):
            node.Z = z
            node.x = x
            node.status = "Solução Candidata"
            self._incumbent_z = z
            return

        # Branch
        node.Z = z
        node.x = x
        node.status = "Ramificado"

        j = _select_branch_variable(x, self.model)
        v = x[j]

        # Lower child: ub_j = floor(v)
        lower_bounds = list(node.bounds)
        lb_j, ub_j = lower_bounds[j]
        lower_bounds[j] = (lb_j, math.floor(v))
        lower_child = BBNode(
            id=self._next_id,
            parent_id=node.id,
            bounds=lower_bounds,
            branch_constraints=_effective_branch_constraints(
                lower_bounds, self.model.bounds, self.model.var_names
            ),
        )
        self._next_id += 1

        # Upper child: lb_j = ceil(v)
        upper_bounds = list(node.bounds)
        lb_j, ub_j = upper_bounds[j]
        upper_bounds[j] = (math.ceil(v), ub_j)
        upper_child = BBNode(
            id=self._next_id,
            parent_id=node.id,
            bounds=upper_bounds,
            branch_constraints=_effective_branch_constraints(
                upper_bounds, self.model.bounds, self.model.var_names
            ),
        )
        self._next_id += 1

        # Add lower first, then upper.
        # DFS (pop from right): upper is explored first unless we reverse -
        # spec says lower is explored first in DFS, so push upper first.
        if self.strategy == "dfs":
            queue.append(upper_child)
            queue.append(lower_child)
        else:  # bfs: popleft, so append lower first → lower explored first
            queue.append(lower_child)
            queue.append(upper_child)

    def _mark_incumbent(self) -> None:
        """Mark the best candidate node as the incumbent with status 'Solução Ótima'."""
        best_node: BBNode | None = None
        best_z = -math.inf if self.model.sense == "max" else math.inf

        for node in self.nodes:
            if node.status != "Solução Candidata":
                continue
            if node.Z is None:
                continue
            if self.model.sense == "max":
                if node.Z > best_z:
                    best_z = node.Z
                    best_node = node
            else:
                if node.Z < best_z:
                    best_z = node.Z
                    best_node = node

        if best_node is not None:
            best_node.is_incumbent = True
            best_node.status = "Solução Ótima"
