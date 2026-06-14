"""Command-line interface for the Parte 4 exercises."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from maxflow import run as run_maxflow
from mst import run as run_mst


def main() -> None:
    """Parse arguments and dispatch to the selected exercise."""
    parser = argparse.ArgumentParser(
        description="Solver for Parte 4 exercises (MST and max flow)."
    )
    parser.add_argument(
        "--exercicio",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help="Exercise number: 1 or 2 (MST), 3 (max flow).",
    )
    parser.add_argument(
        "--prim-start",
        type=int,
        default=1,
        metavar="NODE",
        help="Starting node for Prim's algorithm (default: 1, MST exercises only).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        metavar="PATH",
        help="Path for JSON solution export (optional).",
    )
    args = parser.parse_args()

    if args.exercicio in (1, 2):
        run_mst(args.exercicio, prim_start=args.prim_start, json_path=args.json_out)
    else:
        run_maxflow(json_path=args.json_out)


if __name__ == "__main__":
    main()
