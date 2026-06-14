"""Command-line interface for the Parte 3 optimisation exercises."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python run_parte3.py` from the parte3/ directory
sys.path.insert(0, str(Path(__file__).parent))

from transporte import run as run_transporte
from designacao import run as run_designacao
from investimento import run as run_investimento


def main() -> None:
    """Parse arguments and dispatch to the selected exercise."""
    parser = argparse.ArgumentParser(
        description="Solver for Parte 3 exercises (transport, assignment, investment)."
    )
    parser.add_argument(
        "--exercicio",
        type=int,
        choices=[4, 5, 6],
        required=True,
        help="Exercise number: 4 (transport), 5 (assignment), or 6 (investment).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        metavar="PATH",
        help="Path for the JSON solution export (optional).",
    )
    args = parser.parse_args()

    runners = {
        4: run_transporte,
        5: run_designacao,
        6: run_investimento,
    }
    runners[args.exercicio](json_path=args.json_out)


if __name__ == "__main__":
    main()
