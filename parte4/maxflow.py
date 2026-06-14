"""Edmonds-Karp max-flow algorithm with step logging and min-cut computation."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path

import networkx as nx

from formatting import (
    print_flow_by_arc,
    print_flow_conservation,
    print_min_cut,
    print_path_steps,
    print_section,
    print_subsection,
)
from graphs import G3_ARCS, G3_NODES, G3_SINK, G3_SOURCE


def edmonds_karp(
    arcs: list[tuple[int, int, int]],
    source: int,
    sink: int,
) -> dict:
    """Edmonds-Karp (BFS-based Ford-Fulkerson) max-flow algorithm.

    BFS neighbours are visited in ascending node-index order for determinism.

    Returns a dict with keys: max_flow, paths, arc_flows, min_cut.
    """
    # Residual and original capacities
    cap: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    orig_cap: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    # Neighbour set in residual graph (forward + reverse arcs)
    neighbors: dict[int, set[int]] = defaultdict(set)

    for u, v, c in arcs:
        cap[u][v] += c
        orig_cap[u][v] += c
        neighbors[u].add(v)
        neighbors[v].add(u)

    flow = 0
    paths: list[dict] = []
    iteration = 0

    while True:
        # BFS from source to find a shortest augmenting path
        parent: dict[int, int] = {}
        visited: set[int] = {source}
        queue: deque[int] = deque([source])

        while queue:
            u = queue.popleft()
            if u == sink:
                break
            for v in sorted(neighbors[u]):
                if v not in visited and cap[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)

        if sink not in parent:
            break

        # Reconstruct path from source to sink
        path_nodes: list[int] = []
        node = sink
        while node != source:
            path_nodes.append(node)
            node = parent[node]
        path_nodes.append(source)
        path_nodes.reverse()

        # Bottleneck capacity along the path
        bottleneck = min(
            cap[path_nodes[i]][path_nodes[i + 1]]
            for i in range(len(path_nodes) - 1)
        )

        # Update residual capacities
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            cap[u][v] -= bottleneck
            cap[v][u] += bottleneck

        flow += bottleneck
        iteration += 1
        paths.append({
            "iteration": iteration,
            "path": path_nodes,
            "bottleneck": bottleneck,
            "cumulative_flow": flow,
        })

    # Compute arc flows: flow[u][v] = orig_cap[u][v] - remaining cap[u][v]
    arc_flows: list[dict] = []
    for u, v, c in arcs:
        f = orig_cap[u][v] - cap[u][v]
        arc_flows.append({"u": u, "v": v, "flow": f, "capacity": c})

    # Min-cut: BFS on residual graph from source
    reachable: set[int] = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in sorted(neighbors[u]):
            if v not in reachable and cap[u][v] > 0:
                reachable.add(v)
                queue.append(v)

    cut_arcs: list[tuple[int, int, int]] = sorted(
        (u, v, int(orig_cap[u][v]))
        for u in reachable
        for v in neighbors[u]
        if v not in reachable and orig_cap[u][v] > 0
    )
    cut_capacity = sum(c for _, _, c in cut_arcs)

    return {
        "max_flow": flow,
        "paths": paths,
        "arc_flows": arc_flows,
        "min_cut": {
            "source_side": sorted(reachable),
            "cut_arcs": cut_arcs,
            "total_capacity": cut_capacity,
        },
    }


def _verify_maxflow(
    arcs: list[tuple[int, int, int]],
    nodes: list[int],
    source: int,
    sink: int,
    our_flow: int,
) -> int:
    """Verify max-flow value against NetworkX.  Raises ValueError on mismatch."""
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for u, v, c in arcs:
        G.add_edge(u, v, capacity=c)
    nx_flow_value, _ = nx.maximum_flow(G, source, sink)
    if our_flow != nx_flow_value:
        raise ValueError(
            f"Max flow mismatch: our={our_flow}, networkx={nx_flow_value}"
        )
    return nx_flow_value


def _export_json(sol: dict, nx_flow: int, path: str | Path) -> None:
    """Write the max-flow solution to JSON."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    mc = sol["min_cut"]
    record = {
        "exercicio": 3,
        "fonte": G3_SOURCE,
        "sumidouro": G3_SINK,
        "caminhos_aumentadores": [
            {
                "iteracao": p["iteration"],
                "caminho": p["path"],
                "gargalo": p["bottleneck"],
                "fluxo_acumulado": p["cumulative_flow"],
            }
            for p in sol["paths"]
        ],
        "fluxo_maximo": sol["max_flow"],
        "fluxo_por_arco": [
            {
                "origem": af["u"],
                "destino": af["v"],
                "fluxo": af["flow"],
                "capacidade": af["capacity"],
            }
            for af in sol["arc_flows"]
        ],
        "corte_minimo": {
            "lado_fonte": mc["source_side"],
            "arcos": [[u, v, c] for u, v, c in mc["cut_arcs"]],
            "soma_capacidades": mc["total_capacity"],
        },
        "verificacao": {
            "networkx_fluxo": nx_flow,
            "ok": True,
        },
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)


def run(json_path: str | Path | None = None) -> None:
    """Run Edmonds-Karp for Exercise 3 and print the results."""
    print_section(
        f"Exercicio 3 - Fluxo Maximo - Edmonds-Karp "
        f"(fonte: {G3_SOURCE}, sumidouro: {G3_SINK})"
    )

    sol = edmonds_karp(G3_ARCS, G3_SOURCE, G3_SINK)

    print_subsection("Caminhos aumentadores")
    print_path_steps(sol["paths"])

    print_subsection("Fluxo maximo")
    print(f"  {sol['max_flow']}")

    print_subsection("Fluxo por arco")
    print_flow_by_arc(sol["arc_flows"])

    print_subsection("Conservacao de fluxo nos nos intermediarios")
    print_flow_conservation(G3_NODES, sol["arc_flows"], G3_SOURCE, G3_SINK)

    mc = sol["min_cut"]
    print_subsection("Corte minimo")
    print_min_cut(
        mc["source_side"],
        mc["cut_arcs"],
        mc["total_capacity"],
        sol["max_flow"],
    )

    nx_flow = _verify_maxflow(G3_ARCS, G3_NODES, G3_SOURCE, G3_SINK, sol["max_flow"])
    print_subsection("Verificacao NetworkX")
    print(f"  Fluxo maximo NetworkX: {nx_flow}  [OK]")

    if json_path is not None:
        _export_json(sol, nx_flow, json_path)
        print(f"\n  Solucao exportada para: {json_path}")
