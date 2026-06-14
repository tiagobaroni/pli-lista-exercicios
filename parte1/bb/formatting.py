"""Pure formatting layer: number formatting, node boxes, JSON export."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from bb.model import BBNode, MILPModel

# Statuses for which Z and variable values are shown in the text box.
# Pruned nodes ("Solução Infactível", "Inferior a melhor já obtida") show Status only.
_SHOW_SOLUTION_STATUSES: frozenset[str] = frozenset({
    "Ramificado",
    "Solução Candidata",
    "Solução Ótima",
})


def format_number(value: float, is_objective: bool = False) -> str:
    """Format a float using Brazilian decimal conventions.

    Parameters
    ----------
    value:
        The number to format.
    is_objective:
        If True, always use exactly two decimal places (for Z).
        If False, use no decimals for exact integers, up to 4 for fractions
        (trailing zeros removed).
    """
    if is_objective:
        return f"{value:.2f}".replace(".", ",")

    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))

    # Up to 4 decimal places, strip trailing zeros
    formatted = f"{value:.4f}".rstrip("0").rstrip(".")
    return formatted.replace(".", ",")


def format_node_box(node: BBNode, model: MILPModel) -> str:
    """Render a single B&B node as a formatted text box.

    Parameters
    ----------
    node:
        The node to render.
    model:
        The MILP model (provides variable names).
    """
    lines: list[str] = []
    lines.append(f"Subproblema {node.id}")

    if node.id != 0:
        constraints_str = ", ".join(node.branch_constraints)
        lines.append(f"  Ramo: {constraints_str}")

    if node.status in _SHOW_SOLUTION_STATUSES and node.Z is not None:
        lines.append(f"  Z  = {format_number(node.Z, is_objective=True)}")

    if node.status in _SHOW_SOLUTION_STATUSES and node.x is not None:
        for name, val in zip(model.var_names, node.x):
            lines.append(f"  {name} = {format_number(float(val))}")

    lines.append(f"  Status: {node.status}")
    return "\n".join(lines)


def format_tree(nodes: list[BBNode], model: MILPModel) -> str:
    """Render all nodes in creation order as a sequence of boxes.

    Parameters
    ----------
    nodes:
        All nodes from the solver, in creation (id) order.
    model:
        The MILP model.
    """
    separator = "\n" + "-" * 40 + "\n"
    return separator.join(format_node_box(n, model) for n in nodes)


def export_json(nodes: list[BBNode], model: MILPModel, path: str | Path) -> None:
    """Export the B&B tree to a JSON file.

    Parameters
    ----------
    nodes:
        All nodes from the solver.
    model:
        The MILP model (provides variable names).
    path:
        Destination file path. Parent directories are created if needed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for node in nodes:
        record: dict = {
            "id": node.id,
            "parent_id": node.parent_id,
            "branch": node.branch_constraints,
            "relax_status": "optimal" if node.Z is not None else "infeasible",
            "Z": node.Z,
            "x": (
                {name: float(v) for name, v in zip(model.var_names, node.x)}
                if node.x is not None else None
            ),
            "node_status": node.status,
            "is_incumbent": node.is_incumbent,
        }
        records.append(record)

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
