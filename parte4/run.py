"""Command-line interface for the Parte 4 exercises."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from maxflow import run as run_maxflow
from mst import run as run_mst


def _plot_mst(exercise: int, output_path: str) -> None:
    """Compute MST solution and save graph image to *output_path*."""
    from graphs import G1_EDGES, G1_NODES, G2_EDGES, G2_NODES
    from mst import kruskal
    from plot import plot_mst

    edges = G1_EDGES if exercise == 1 else G2_EDGES
    nodes = G1_NODES if exercise == 1 else G2_NODES
    k_result = kruskal(edges, nodes)
    plot_mst(exercise, edges, nodes,
             k_result["tree_edges"], k_result["total_weight"], output_path)
    print(f"\n  Imagem salva em: {output_path}")


def _plot_maxflow(output_path: str) -> None:
    """Compute max-flow solution and save graph image to *output_path*."""
    from graphs import G3_ARCS, G3_NODES, G3_SINK, G3_SOURCE
    from maxflow import edmonds_karp
    from plot import plot_maxflow

    sol = edmonds_karp(G3_ARCS, G3_SOURCE, G3_SINK)
    plot_maxflow(G3_ARCS, G3_NODES, sol["arc_flows"],
                 sol["max_flow"], G3_SOURCE, G3_SINK, output_path)
    print(f"\n  Imagem salva em: {output_path}")


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
    parser.add_argument(
        "--plot",
        type=str,
        default=None,
        metavar="PATH",
        help="Save solution graph image to PATH (PNG).",
    )
    args = parser.parse_args()

    if args.exercicio in (1, 2):
        run_mst(args.exercicio, prim_start=args.prim_start, json_path=args.json_out)
        if args.plot is not None:
            _plot_mst(args.exercicio, args.plot)
    else:
        run_maxflow(json_path=args.json_out)
        if args.plot is not None:
            _plot_maxflow(args.plot)


if __name__ == "__main__":
    main()
