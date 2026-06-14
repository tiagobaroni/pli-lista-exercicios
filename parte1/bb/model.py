"""MILP model dataclass and exercise builders for the Branch-and-Bound solver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

import numpy as np


@dataclass
class MILPModel:
    """Represents a Mixed-Integer Linear Program in standard form.

    All constraints are stored as A_ub @ x <= b_ub.
    For maximisation, the caller negates c before passing it here;
    the sense field records the original direction for reporting.
    """

    c: np.ndarray
    A_ub: np.ndarray
    b_ub: np.ndarray
    bounds: list[tuple[float, float | None]]
    integers: list[int]
    sense: Literal["max", "min"]
    var_names: list[str]
    name: str


@dataclass
class RelaxResult:
    """Result of solving an LP relaxation at a single B&B node."""

    feasible: bool
    Z: float | None        # objective in original sense (not negated)
    x: np.ndarray | None
    raw_status: str


@dataclass
class BBNode:
    """A single node in the Branch-and-Bound tree."""

    id: int
    parent_id: int | None
    bounds: list[tuple[float, float | None]]
    branch_constraints: list[str]
    status: str = ""
    Z: float | None = None  # objective in original sense
    x: np.ndarray | None = None
    is_incumbent: bool = False


def build_exercicio_1() -> MILPModel:
    """Build Exercise 1: pure-integer maximisation.

    max  z = x1 + 5x2 + 9x3 + 5x4
    s.t.  x1 + 3x2 +  9x3 + 6x4 <= 16
          6x1 + 6x2 +  0x3 + 7x4 <= 19
          7x1 + 8x2 + 18x3 + 3x4 <= 44
          x1, x2, x3, x4 >= 0, integer
    """
    c = np.array([-1.0, -5.0, -9.0, -5.0])  # negated for minimisation
    A_ub = np.array([
        [1.0, 3.0,  9.0, 6.0],
        [6.0, 6.0,  0.0, 7.0],
        [7.0, 8.0, 18.0, 3.0],
    ])
    b_ub = np.array([16.0, 19.0, 44.0])
    bounds = [(0.0, None)] * 4
    return MILPModel(
        c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
        integers=[0, 1, 2, 3], sense="max",
        var_names=["x1", "x2", "x3", "x4"], name="Exercício 1",
    )


def build_exercicio_2() -> MILPModel:
    """Build Exercise 2: mixed-integer maximisation (x3 continuous).

    max  z = 7x1 + 9x2 + x3 + 6x4
    s.t.  8x1 + 2x2 + 4x3 + 2x4 <= 16
          4x1 + 8x2 + 2x3 + 0x4 <= 20
          7x1 + 0x2 + 6x3 + 2x4 <= 11
          x1, x2, x4 >= 0 integer; x3 >= 0 continuous
    """
    c = np.array([-7.0, -9.0, -1.0, -6.0])
    A_ub = np.array([
        [8.0, 2.0, 4.0, 2.0],
        [4.0, 8.0, 2.0, 0.0],
        [7.0, 0.0, 6.0, 2.0],
    ])
    b_ub = np.array([16.0, 20.0, 11.0])
    bounds = [(0.0, None)] * 4
    return MILPModel(
        c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
        integers=[0, 1, 3], sense="max",
        var_names=["x1", "x2", "x3", "x4"], name="Exercício 2",
    )


def build_exercicio_4() -> MILPModel:
    """Build Exercise 4: mixed-integer minimisation (x2 continuous).

    min  z = 2x1 + 3x2 + 5x3
    s.t.  x1 + 2x2 + 3x3 >= 7   -> -x1 - 2x2 - 3x3 <= -7
          3x1 + 2x2 + 3x3 >= 11  -> -3x1 - 2x2 - 3x3 <= -11
          x1, x3 >= 0 integer; x2 >= 0 continuous
    """
    c = np.array([2.0, 3.0, 5.0])
    A_ub = np.array([
        [-1.0, -2.0, -3.0],
        [-3.0, -2.0, -3.0],
    ])
    b_ub = np.array([-7.0, -11.0])
    bounds = [(0.0, None)] * 3
    return MILPModel(
        c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
        integers=[0, 2], sense="min",
        var_names=["x1", "x2", "x3"], name="Exercício 4",
    )


EXERCISE_BUILDERS: dict[int, Callable[[], MILPModel]] = {
    1: build_exercicio_1,
    2: build_exercicio_2,
    4: build_exercicio_4,
}
