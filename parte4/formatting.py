"""Console formatting utilities for Parte 4: graphs, MST, and max flow."""

from __future__ import annotations


def print_section(title: str) -> None:
    """Print a top-level section banner."""
    width = max(len(title) + 6, 60)
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subsection(title: str) -> None:
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def print_kruskal_steps(steps: list[dict]) -> None:
    """Print Kruskal decision table."""
    print(f"  {'#':>4}  {'Aresta':^12}  {'Peso':>4}  Decisao")
    print("  " + "-" * 4 + "  " + "-" * 12 + "  " + "-" * 4 + "  " + "-" * 10)
    for i, s in enumerate(steps, 1):
        edge_str = f"({s['edge'][0]}, {s['edge'][1]})"
        decision = "Aceita" if s["accepted"] else "Rejeitada"
        print(f"  {i:>4}  {edge_str:^12}  {s['weight']:>4}  {decision}")


def print_prim_steps(steps: list[dict], start_node: int) -> None:
    """Print Prim expansion table."""
    print(f"  No inicial: {start_node}")
    print()
    print(f"  {'Passo':>5}  {'No adicionado':>13}  {'De no':>5}  {'Aresta':^12}  {'Peso':>4}")
    print("  " + "-" * 5 + "  " + "-" * 13 + "  " + "-" * 5 + "  " + "-" * 12 + "  " + "-" * 4)
    for i, s in enumerate(steps, 1):
        u, v = s["from_node"], s["node_added"]
        edge_str = f"({min(u, v)}, {max(u, v)})"
        print(f"  {i:>5}  {v:>13}  {u:>5}  {edge_str:^12}  {s['weight']:>4}")


def print_tree_edges(tree_edges: list[tuple[int, int, int]], total_weight: int, label: str) -> None:
    """Print the final MST edge list and total weight."""
    edges_str = ", ".join(f"({u},{v})" for u, v, _ in tree_edges)
    print(f"\n  Arestas da arvore ({label}): {edges_str}")
    print(f"  Peso total: {total_weight}")


def print_path_steps(steps: list[dict]) -> None:
    """Print Edmonds-Karp augmenting path table."""
    if not steps:
        print("  Nenhum caminho aumentador encontrado.")
        return
    max_path_len = max(
        len(" -> ".join(str(n) for n in s["path"])) for s in steps
    )
    col_path = max(max_path_len, 18)

    header = (
        f"  {'Iter':>4}  {'Caminho aumentador':<{col_path}}  "
        f"{'Gargalo':>7}  {'Fluxo acumulado':>15}"
    )
    sep = "  " + "-" * (len(header) - 2)
    print(header)
    print(sep)
    for s in steps:
        path_str = " -> ".join(str(n) for n in s["path"])
        print(
            f"  {s['iteration']:>4}  {path_str:<{col_path}}  "
            f"{s['bottleneck']:>7}  {s['cumulative_flow']:>15}"
        )


def print_flow_by_arc(arc_flows: list[dict]) -> None:
    """Print flow per arc table."""
    print(f"  {'Origem':>6}  {'Destino':>7}  {'Fluxo':>5}  {'Cap':>5}")
    print("  " + "-" * 6 + "  " + "-" * 7 + "  " + "-" * 5 + "  " + "-" * 5)
    for af in arc_flows:
        print(f"  {af['u']:>6}  {af['v']:>7}  {af['flow']:>5}  {af['capacity']:>5}")


def print_flow_conservation(
    nodes: list[int], arc_flows: list[dict], source: int, sink: int
) -> None:
    """Print flow conservation for intermediate nodes."""
    flow_in: dict[int, int] = {n: 0 for n in nodes}
    flow_out: dict[int, int] = {n: 0 for n in nodes}
    for af in arc_flows:
        flow_out[af["u"]] += af["flow"]
        flow_in[af["v"]] += af["flow"]

    intermediate = [n for n in sorted(nodes) if n != source and n != sink]
    print(f"  {'No':>3}  {'Entrada':>7}  {'Saida':>5}  Status")
    print("  " + "-" * 3 + "  " + "-" * 7 + "  " + "-" * 5 + "  " + "-" * 8)
    for n in intermediate:
        balance = flow_in[n] - flow_out[n]
        status = "[OK]" if abs(balance) < 1e-9 else f"ERRO ({balance})"
        print(f"  {n:>3}  {flow_in[n]:>7}  {flow_out[n]:>5}  {status}")


def print_min_cut(
    source_side: list[int],
    cut_arcs: list[tuple[int, int, int]],
    total_capacity: int,
    max_flow: int,
) -> None:
    """Print min-cut information."""
    nodes_str = "{" + ", ".join(str(n) for n in sorted(source_side)) + "}"
    print(f"  Nos no lado da fonte: {nodes_str}")
    print()
    print("  Arcos que cruzam o corte:")
    print(f"  {'Origem':>6}  {'Destino':>7}  {'Capacidade':>10}")
    print("  " + "-" * 6 + "  " + "-" * 7 + "  " + "-" * 10)
    for u, v, cap in cut_arcs:
        print(f"  {u:>6}  {v:>7}  {cap:>10}")
    ok_sym = "[OK]" if total_capacity == max_flow else "ERRO"
    print(f"\n  Soma das capacidades: {total_capacity}  {ok_sym}  (fluxo maximo = {max_flow})")
