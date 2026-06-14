"""Command-line interface for the Parte 1 Branch-and-Bound solver."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python run.py` from the parte1/ directory
sys.path.insert(0, str(Path(__file__).parent))

from bb.formatting import export_json, format_tree, format_number
from bb.model import EXERCISE_BUILDERS
from bb.relaxation import verify_with_milp
from bb.solver import BranchAndBoundSolver


_VERIFY_TOL = 1e-4


def _build_summary(solver: BranchAndBoundSolver, milp_z: float) -> str:
    """Build the end-of-run summary block."""
    model = solver.model
    nodes = solver.nodes
    n_solved = len(nodes)

    incumbent = next((n for n in nodes if n.is_incumbent), None)
    if incumbent is None:
        return f"=== Resultado - {model.name} ===\nNenhuma solução inteira encontrada.\n"

    var_str = ",  ".join(
        f"{name}={format_number(float(v))}"
        for name, v in zip(model.var_names, incumbent.x)
    )
    bb_z_fmt = format_number(incumbent.Z, is_objective=True)
    milp_z_fmt = format_number(milp_z, is_objective=True)

    bb_z_val = incumbent.Z
    if abs(bb_z_val - milp_z) > _VERIFY_TOL:
        raise ValueError(
            f"B&B result {bb_z_val:.6f} diverges from scipy.milp result "
            f"{milp_z:.6f} by more than {_VERIFY_TOL}. Model: {model.name}"
        )

    lines = [
        f"=== Resultado - {model.name} ===",
        f"Nós resolvidos: {n_solved}",
        f"Solução ótima: {var_str}  |  Z = {bb_z_fmt}",
        f"Verificação milp: Z = {milp_z_fmt}  ✓",
    ]
    return "\n".join(lines)


def main() -> None:
    """Parse arguments and run the B&B solver."""
    parser = argparse.ArgumentParser(
        description="Branch-and-Bound solver for Parte 1 MILP exercises."
    )
    parser.add_argument(
        "--exercicio",
        type=int,
        choices=[1, 2, 4],
        required=True,
        help="Exercise number (1, 2, or 4).",
    )
    parser.add_argument(
        "--strategy",
        choices=["dfs", "bfs"],
        default="dfs",
        help="Search strategy: dfs (default) or bfs.",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of nodes to process (default: no limit).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        metavar="PATH",
        help="Path for the JSON tree export.",
    )
    args = parser.parse_args()

    model = EXERCISE_BUILDERS[args.exercicio]()
    solver = BranchAndBoundSolver(
        model=model,
        strategy=args.strategy,
        max_nodes=args.max_nodes,
    )
    nodes = solver.solve()

    print(format_tree(nodes, model))
    print()

    milp_z = verify_with_milp(model)
    print(_build_summary(solver, milp_z))

    if args.json_out:
        export_json(nodes, model, args.json_out)
        print(f"\nÁrvore exportada para: {args.json_out}")


if __name__ == "__main__":
    main()
