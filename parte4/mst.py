"""Prim's and Kruskal's MST algorithms with decision logging."""

from __future__ import annotations

import heapq
import json
from pathlib import Path

import networkx as nx

from formatting import (
    print_kruskal_steps,
    print_prim_steps,
    print_section,
    print_subsection,
    print_tree_edges,
)
from graphs import G1_EDGES, G1_NODES, G2_EDGES, G2_NODES


class UnionFind:
    """Union-Find with path compression and union by rank."""

    def __init__(self, nodes: list[int]) -> None:
        self._parent: dict[int, int] = {n: n for n in nodes}
        self._rank: dict[int, int] = {n: 0 for n in nodes}

    def find(self, x: int) -> int:
        """Find the representative of x with path compression."""
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: int, y: int) -> bool:
        """Unite the sets containing x and y.  Returns True if they were disjoint."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
        return True


def kruskal(edges: list[tuple[int, int, int]], nodes: list[int]) -> dict:
    """Kruskal's MST algorithm.

    Edges are examined in ascending weight order; ties broken by
    (min_endpoint, max_endpoint).  Union-Find detects cycle-forming edges.

    Returns a dict with keys: tree_edges, total_weight, steps.
    Each step dict: {edge, weight, accepted}.
    """
    sorted_edges = sorted(
        edges,
        key=lambda e: (e[2], min(e[0], e[1]), max(e[0], e[1])),
    )
    uf = UnionFind(nodes)
    tree_edges: list[tuple[int, int, int]] = []
    steps: list[dict] = []

    for u, v, w in sorted_edges:
        a, b = min(u, v), max(u, v)
        accepted = uf.union(a, b)
        steps.append({"edge": (a, b), "weight": w, "accepted": accepted})
        if accepted:
            tree_edges.append((a, b, w))

    return {
        "tree_edges": tree_edges,
        "total_weight": sum(e[2] for e in tree_edges),
        "steps": steps,
    }


def prim(
    edges: list[tuple[int, int, int]], nodes: list[int], start: int = 1
) -> dict:
    """Prim's MST algorithm starting from *start*.

    At each step the minimum-weight edge crossing the tree/non-tree cut is
    selected.  Ties broken by (weight, to_node) — the node being added.

    Returns a dict with keys: tree_edges, total_weight, steps, start_node.
    Each step dict: {node_added, from_node, weight}.
    """
    adj: dict[int, list[tuple[int, int]]] = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))

    in_tree: set[int] = {start}
    # Heap entries: (weight, to_node, from_node)
    heap: list[tuple[int, int, int]] = []
    for w, v in adj[start]:
        heapq.heappush(heap, (w, v, start))

    tree_edges: list[tuple[int, int, int]] = []
    steps: list[dict] = []

    while heap and len(in_tree) < len(nodes):
        w, v, u = heapq.heappop(heap)
        if v in in_tree:
            continue
        in_tree.add(v)
        tree_edges.append((min(u, v), max(u, v), w))
        steps.append({"node_added": v, "from_node": u, "weight": w})
        for w2, nbr in adj[v]:
            if nbr not in in_tree:
                heapq.heappush(heap, (w2, nbr, v))

    return {
        "tree_edges": tree_edges,
        "total_weight": sum(e[2] for e in tree_edges),
        "steps": steps,
        "start_node": start,
    }


def _verify_mst(
    edges: list[tuple[int, int, int]],
    nodes: list[int],
    our_weight: int,
) -> int:
    """Verify MST weight against NetworkX.  Raises ValueError on mismatch."""
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    nx_mst = nx.minimum_spanning_tree(G)
    nx_weight = int(sum(d["weight"] for _, _, d in nx_mst.edges(data=True)))
    if our_weight != nx_weight:
        raise ValueError(
            f"MST weight mismatch: our={our_weight}, networkx={nx_weight}"
        )
    return nx_weight


def _export_json(
    exercise: int,
    k_result: dict,
    p_result: dict,
    nx_weight: int,
    path: str | Path,
) -> None:
    """Write MST results to JSON."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "exercicio": exercise,
        "kruskal": {
            "steps": [
                {
                    "aresta": list(s["edge"]),
                    "peso": s["weight"],
                    "decisao": "Aceita" if s["accepted"] else "Rejeitada",
                }
                for s in k_result["steps"]
            ],
            "arvore": [list(e) for e in k_result["tree_edges"]],
            "peso_total": k_result["total_weight"],
        },
        "prim": {
            "no_inicial": p_result["start_node"],
            "steps": [
                {
                    "no_adicionado": s["node_added"],
                    "de_no": s["from_node"],
                    "aresta": [
                        min(s["from_node"], s["node_added"]),
                        max(s["from_node"], s["node_added"]),
                    ],
                    "peso": s["weight"],
                }
                for s in p_result["steps"]
            ],
            "arvore": [list(e) for e in p_result["tree_edges"]],
            "peso_total": p_result["total_weight"],
        },
        "verificacao": {
            "networkx_peso": nx_weight,
            "ok": True,
        },
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)


def run(
    exercise: int,
    prim_start: int = 1,
    json_path: str | Path | None = None,
) -> None:
    """Run Kruskal and Prim for the given exercise and print the results."""
    if exercise == 1:
        edges, nodes = G1_EDGES, G1_NODES
        title = "Exercicio 1 - Arvore Geradora Minima (Grafo 1, 12 nos)"
    elif exercise == 2:
        edges, nodes = G2_EDGES, G2_NODES
        title = "Exercicio 2 - Arvore Geradora Minima (Grafo 2, 15 nos)"
    else:
        raise ValueError(f"Exercicio invalido para MST: {exercise} (esperado 1 ou 2)")

    print_section(title)

    # ---- Kruskal --------------------------------------------------------
    print_subsection("Kruskal - Sequencia de decisoes")
    k_result = kruskal(edges, nodes)
    print_kruskal_steps(k_result["steps"])
    print_subsection("Kruskal - Resultado")
    print_tree_edges(k_result["tree_edges"], k_result["total_weight"], "Kruskal")

    # ---- Prim -----------------------------------------------------------
    print_subsection(f"Prim - Sequencia de expansao (no inicial: {prim_start})")
    p_result = prim(edges, nodes, start=prim_start)
    print_prim_steps(p_result["steps"], prim_start)
    print_subsection("Prim - Resultado")
    print_tree_edges(p_result["tree_edges"], p_result["total_weight"], "Prim")

    # ---- Cross-verification --------------------------------------------
    if k_result["total_weight"] != p_result["total_weight"]:
        raise ValueError(
            f"Kruskal ({k_result['total_weight']}) != Prim ({p_result['total_weight']})"
        )
    nx_weight = _verify_mst(edges, nodes, k_result["total_weight"])

    print_subsection("Verificacao")
    print(f"  Kruskal:  {k_result['total_weight']}")
    print(f"  Prim:     {p_result['total_weight']}")
    print(f"  NetworkX: {nx_weight}  [OK]")

    if json_path is not None:
        _export_json(exercise, k_result, p_result, nx_weight, json_path)
        print(f"\n  Solucao exportada para: {json_path}")
