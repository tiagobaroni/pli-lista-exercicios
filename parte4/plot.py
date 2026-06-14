"""Graph visualization for Parte 4 exercises."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

# ---------------------------------------------------------------------------
# Node positions (pixel coords from the original problem figures).
# Y-axis is inverted in _flip_y() because pixels grow downward while
# matplotlib's y-axis grows upward.
# ---------------------------------------------------------------------------

_POS_G1_RAW: dict[int, tuple[int, int]] = {
    11: (54, 29),   7: (136, 94),  12: (27, 127),   6: (236, 158),
    10: (105, 211), 3: (315, 252),  5: (238, 274),   8: (145, 299),
     1: (401, 309), 9: (189, 317),  4: (289, 353),   2: (377, 403),
}

_POS_G2_RAW: dict[int, tuple[int, int]] = {
    11: (235, 25),  15: (304, 49),  12: (175, 65),   7: (255, 122),
    14: (362, 142), 10: (133, 171),  6: (314, 207),   8: (19, 210),
    13: (397, 247),  5: (206, 252),  9: (106, 259),   3: (314, 290),
     4: (211, 332),  1: (391, 343),  2: (303, 403),
}

_POS_G3_RAW: dict[int, tuple[int, int]] = {
    11: (350, 29),  12: (404, 87),   7: (275, 102),  10: (337, 177),
     6: (179, 182),  8: (316, 253),  5: (205, 267),   3: (113, 275),
     9: (269, 280),  4: (166, 337),  1: (28, 344),    2: (78, 404),
}

# ---------------------------------------------------------------------------
# Visual constants
# ---------------------------------------------------------------------------

_COLOR_NODE      = "#4DB8C8"   # turquoise (regular nodes)
_COLOR_NODE_SP   = "#E07030"   # orange    (source / sink)
_COLOR_EDGE_GRAY = "#BBBBBB"   # light gray (background edges)
_COLOR_EDGE_HL   = "#8B1010"   # dark red   (solution edges)
_COLOR_LBL_GRAY  = "#999999"
_COLOR_LBL_HL    = "#6B0000"

_DPI        = 200
_FIG_W      = 7.0
_FIG_H      = 7.0
_NODE_SIZE  = 550
_FONT_NODE  = 9
_FONT_EDGE  = 7
_W_THIN     = 1.0
_W_THICK    = 2.8
_BBOX_BG    = {"facecolor": "white", "alpha": 0.65, "edgecolor": "none", "pad": 1}
_BBOX_HL    = {"facecolor": "white", "alpha": 0.85, "edgecolor": "none", "pad": 1}


def _flip_y(raw: dict[int, tuple[int, int]]) -> dict[int, tuple[float, float]]:
    """Convert pixel coords (y downward) to matplotlib coords (y upward)."""
    return {n: (float(x), float(-y)) for n, (x, y) in raw.items()}


def _save(fig: plt.Figure, output_path: str | Path) -> None:
    """Save *fig* to *output_path*; create parent directories as needed."""
    out = Path(output_path)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=_DPI, bbox_inches="tight", facecolor="white")
    except OSError as exc:
        raise OSError(f"Não foi possível salvar a imagem em '{out}': {exc}") from exc
    finally:
        plt.close(fig)


def plot_mst(
    exercise: int,
    edges: list[tuple[int, int, int]],
    nodes: list[int],
    tree_edges: list[tuple[int, int, int]],
    total_weight: int,
    output_path: str | Path,
) -> None:
    """Save a PNG of the undirected graph with the MST highlighted.

    Non-MST edges are drawn in light gray; MST edges are overlaid in dark red
    with thick lines.  All weights are labelled.  Node positions are fixed to
    match the original problem figures.
    """
    pos_raw = _POS_G1_RAW if exercise == 1 else _POS_G2_RAW
    pos = _flip_y(pos_raw)

    G = nx.Graph()
    G.add_nodes_from(nodes)
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    tree_set: set[frozenset[int]] = {frozenset({u, v}) for u, v, _ in tree_edges}
    bg_edgelist = [(u, v) for u, v in G.edges() if frozenset({u, v}) not in tree_set]
    hl_edgelist = [(u, v) for u, v in G.edges() if frozenset({u, v}) in tree_set]

    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    ax.set_axis_off()

    # Non-MST edges and their weight labels
    nx.draw_networkx_edges(G, pos, edgelist=bg_edgelist,
                           width=_W_THIN, edge_color=_COLOR_EDGE_GRAY, ax=ax)
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): G[u][v]["weight"] for u, v in bg_edgelist},
        font_size=_FONT_EDGE, font_color=_COLOR_LBL_GRAY, rotate=False,
        bbox=_BBOX_BG, ax=ax,
    )

    # MST edges on top with their weight labels
    nx.draw_networkx_edges(G, pos, edgelist=hl_edgelist,
                           width=_W_THICK, edge_color=_COLOR_EDGE_HL, ax=ax)
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): G[u][v]["weight"] for u, v in hl_edgelist},
        font_size=_FONT_EDGE, font_color=_COLOR_LBL_HL, rotate=False,
        bbox=_BBOX_HL, ax=ax,
    )

    # Nodes on top of everything
    nx.draw_networkx_nodes(G, pos, node_size=_NODE_SIZE,
                           node_color=_COLOR_NODE, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="white",
                            font_size=_FONT_NODE, font_weight="bold", ax=ax)

    n_nodes = 12 if exercise == 1 else 15
    ax.set_title(
        f"Exercício {exercise} - Árvore Geradora Mínima"
        f" (Grafo {exercise}, {n_nodes} nós)\n"
        f"Peso total da AGM: {total_weight}",
        fontsize=11, pad=8,
    )
    _save(fig, output_path)


def plot_maxflow(
    arcs: list[tuple[int, int, int]],
    nodes: list[int],
    arc_flows: list[dict],
    max_flow: int,
    source: int,
    sink: int,
    output_path: str | Path,
) -> None:
    """Save a PNG of the directed graph with the max-flow solution highlighted.

    Arcs carrying positive flow are drawn in dark red with 'fluxo/capacidade'
    labels.  Source and sink nodes are coloured orange.  Node positions are
    fixed to match the original problem figures.
    """
    pos = _flip_y(_POS_G3_RAW)

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for u, v, c in arcs:
        G.add_edge(u, v, capacity=c)

    flow_map: dict[tuple[int, int], int] = {
        (af["u"], af["v"]): af["flow"] for af in arc_flows
    }
    cap_map: dict[tuple[int, int], int] = {(u, v): c for u, v, c in arcs}

    bg_arcs = [(u, v) for u, v in G.edges() if flow_map.get((u, v), 0) == 0]
    hl_arcs = [(u, v) for u, v in G.edges() if flow_map.get((u, v), 0) > 0]

    node_list = list(G.nodes())
    node_colors: list[str] = [
        _COLOR_NODE_SP if n in (source, sink) else _COLOR_NODE
        for n in node_list
    ]

    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    ax.set_axis_off()

    # Background arcs (zero flow) in gray
    nx.draw_networkx_edges(G, pos, edgelist=bg_arcs,
                           width=_W_THIN, edge_color=_COLOR_EDGE_GRAY,
                           arrows=True, arrowsize=12,
                           node_size=_NODE_SIZE, ax=ax)
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): cap_map[u, v] for u, v in bg_arcs},
        font_size=_FONT_EDGE, font_color=_COLOR_LBL_GRAY, rotate=False,
        bbox=_BBOX_BG, ax=ax,
    )

    # Flow arcs in dark red with "fluxo/capacidade" labels
    nx.draw_networkx_edges(G, pos, edgelist=hl_arcs,
                           width=_W_THICK, edge_color=_COLOR_EDGE_HL,
                           arrows=True, arrowsize=16,
                           node_size=_NODE_SIZE, ax=ax)
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={
            (u, v): f"{flow_map[u, v]}/{cap_map[u, v]}" for u, v in hl_arcs
        },
        font_size=_FONT_EDGE, font_color=_COLOR_LBL_HL, rotate=False,
        bbox=_BBOX_HL, ax=ax,
    )

    # Nodes
    nx.draw_networkx_nodes(G, pos, nodelist=node_list,
                           node_size=_NODE_SIZE, node_color=node_colors, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="white",
                            font_size=_FONT_NODE, font_weight="bold", ax=ax)

    ax.set_title(
        f"Exercício 3 - Fluxo Máximo - Edmonds-Karp\n"
        f"Fluxo máximo: {max_flow}  |  Fonte: {source}  |  Sumidouro: {sink}",
        fontsize=11, pad=8,
    )
    _save(fig, output_path)
