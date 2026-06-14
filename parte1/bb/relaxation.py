"""LP relaxation solver and MILP cross-verification for B&B nodes."""

from __future__ import annotations

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

from bb.model import MILPModel, RelaxResult

_INTEGRALITY_TOL = 1e-6
_VERIFY_TOL = 1e-4


def solve_relaxation(model: MILPModel, bounds: list[tuple[float, float | None]]) -> RelaxResult:
    """Solve the LP relaxation of *model* with the given variable bounds.

    Parameters
    ----------
    model:
        The MILP model (c already negated for max→min).
    bounds:
        Per-variable (lb, ub) pairs for this node; ub=None means +inf.

    Returns
    -------
    RelaxResult
        feasible=True and Z in original sense when optimal; feasible=False otherwise.

    Raises
    ------
    RuntimeError
        When linprog returns a status other than optimal (0) or infeasible (2).
    """
    scipy_bounds = [(lb, ub if ub is not None else np.inf) for lb, ub in bounds]
    result = linprog(
        c=model.c,
        A_ub=model.A_ub,
        b_ub=model.b_ub,
        bounds=scipy_bounds,
        method="highs",
    )

    if result.status == 0:  # optimal
        raw_z = float(result.fun)
        z = -raw_z if model.sense == "max" else raw_z
        return RelaxResult(feasible=True, Z=z, x=result.x.copy(), raw_status="optimal")

    if result.status == 2:  # infeasible
        return RelaxResult(feasible=False, Z=None, x=None, raw_status="infeasible")

    if result.status == 3:  # unbounded
        raise RuntimeError(
            f"LP relaxation is unbounded at node (linprog status=3). "
            f"Model: {model.name}"
        )

    raise RuntimeError(
        f"linprog returned unexpected status {result.status}: {result.message}. "
        f"Model: {model.name}"
    )


def verify_with_milp(model: MILPModel) -> float:
    """Solve the MILP exactly with scipy.optimize.milp and return Z in original sense.

    Used to cross-verify the B&B result.

    Parameters
    ----------
    model:
        The MILP model with original bounds.

    Returns
    -------
    float
        Optimal objective value in original sense.

    Raises
    ------
    RuntimeError
        When milp does not find an optimal solution.
    """
    n = len(model.c)
    integrality = np.zeros(n)
    for j in model.integers:
        integrality[j] = 1.0

    lbs = np.array([b[0] for b in model.bounds], dtype=float)
    ubs = np.array([b[1] if b[1] is not None else np.inf for b in model.bounds], dtype=float)

    constraints = LinearConstraint(model.A_ub, lb=-np.inf, ub=model.b_ub)
    variable_bounds = Bounds(lb=lbs, ub=ubs)

    result = milp(
        c=model.c,
        constraints=constraints,
        integrality=integrality,
        bounds=variable_bounds,
    )

    if result.status != 0:
        raise RuntimeError(
            f"scipy.optimize.milp did not find an optimal solution "
            f"(status={result.status}: {result.message}). Model: {model.name}"
        )

    raw_z = float(result.fun)
    return -raw_z if model.sense == "max" else raw_z
