"""Exercise 4 - Unbalanced transportation problem (Deise-Luzia distribution centres).

Three supply centres (C1, C2, C3) serve eleven real warehouses (W1-W11).
Total supply (1650) exceeds total demand (1218), so a dummy destination absorbs
the surplus.  The model is solved as a balanced LP with equality constraints.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from formatting import format_number, print_matrix, print_section, print_subsection

# ---------------------------------------------------------------------------
# Problem data
# ---------------------------------------------------------------------------

DISTANCES: np.ndarray = np.array([
    [10, 22, 29, 45, 11, 31, 42, 61, 36, 21, 45],   # C1
    [25, 35, 17, 38,  9, 17, 65, 45, 42,  5, 41],   # C2
    [18, 19, 22, 29, 24, 54, 39, 78, 51, 14, 38],   # C3
], dtype=float)

SUPPLY: np.ndarray = np.array([500.0, 750.0, 400.0])
DEMAND: np.ndarray = np.array(
    [112.0, 85.0, 138.0, 146.0, 77.0, 89.0, 101.0, 215.0, 53.0, 49.0, 153.0]
)
UNIT_COST: float = 0.50

CENTERS: list[str] = ["C1", "C2", "C3"]
WAREHOUSES: list[str] = [f"W{i + 1}" for i in range(11)]
DUMMY_LABEL: str = "Ficticio"


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

def solve() -> dict:
    """Solve the balanced transportation LP with linprog (HiGHS).

    Returns
    -------
    dict
        allocation (3×11 ndarray for real warehouses),
        dummy_allocation (3,) for the dummy destination,
        total_cost (float, sum of unit_cost × distance × quantity over real routes),
        status (str from linprog).
    """
    n_i = len(CENTERS)           # 3
    n_j_real = len(WAREHOUSES)   # 11
    n_j = n_j_real + 1           # 12  (11 real + 1 dummy)

    dummy_demand = float(SUPPLY.sum() - DEMAND.sum())   # 432

    # Cost matrix 3×12: unit_cost × distance for real columns, 0 for dummy
    costs_full = np.zeros((n_i, n_j))
    costs_full[:, :n_j_real] = UNIT_COST * DISTANCES
    c = costs_full.flatten()

    demand_full = np.append(DEMAND, dummy_demand)

    # Equality constraint matrix: (n_i + n_j) × (n_i * n_j)
    n_vars = n_i * n_j
    A_eq = np.zeros((n_i + n_j, n_vars))
    b_eq = np.zeros(n_i + n_j)

    # Supply constraints: for each centre i, sum over destinations j
    for i in range(n_i):
        for j in range(n_j):
            A_eq[i, i * n_j + j] = 1.0
        b_eq[i] = SUPPLY[i]

    # Demand constraints: for each destination j, sum over centres i
    for j in range(n_j):
        for i in range(n_i):
            A_eq[n_i + j, i * n_j + j] = 1.0
        b_eq[n_i + j] = demand_full[j]

    bounds = [(0.0, None)] * n_vars
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

    if result.status != 0:
        raise RuntimeError(
            f"linprog retornou status {result.status}: {result.message}"
        )

    x = result.x.reshape(n_i, n_j)
    allocation = x[:, :n_j_real]
    dummy_alloc = x[:, n_j_real]

    total_cost = float(np.sum(costs_full[:, :n_j_real] * allocation))

    return {
        "allocation": allocation,
        "dummy_allocation": dummy_alloc,
        "total_cost": total_cost,
        "status": result.message,
    }


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def run(json_path: str | Path | None = None) -> None:
    """Print model data, solve, and display solution for Exercise 4."""
    n_i = len(CENTERS)
    n_j_real = len(WAREHOUSES)
    n_j = n_j_real + 1
    dummy_demand = float(SUPPLY.sum() - DEMAND.sum())

    print_section("Exercicio 4 - Problema de Transporte (Deise-Luzia)")

    # ---- Input data --------------------------------------------------------
    print_subsection("Dados de entrada")
    print(f"  Centros de distribuicao: {', '.join(CENTERS)}")
    print(f"  Armazens: {', '.join(WAREHOUSES)}")
    supply_str = "  ".join(f"{CENTERS[i]}={int(SUPPLY[i])}" for i in range(n_i))
    print(f"  Capacidades (oferta):  {supply_str}  | Total = {int(SUPPLY.sum())}")
    demand_str = "  ".join(f"{WAREHOUSES[j]}={int(DEMAND[j])}" for j in range(n_j_real))
    print(f"  Demandas: {demand_str}")
    print(f"  Total demanda = {int(DEMAND.sum())}  |  "
          f"Excesso (destino ficticio) = {int(dummy_demand)}")

    print_subsection("Tabela de distancias d_ij (km)")
    print_matrix(DISTANCES.tolist(), CENTERS, WAREHOUSES, decimals=0)

    costs_real = UNIT_COST * DISTANCES
    print_subsection("Tabela de custos c_ij = 0,50 x d_ij")
    print_matrix(costs_real.tolist(), CENTERS, WAREHOUSES, decimals=2)

    costs_full = np.zeros((n_i, n_j))
    costs_full[:, :n_j_real] = costs_real
    print_subsection("Problema balanceado: custo completo incluindo coluna ficticia (custo 0)")
    print_matrix(
        costs_full.tolist(), CENTERS, WAREHOUSES + [DUMMY_LABEL], decimals=2
    )

    demand_full = np.append(DEMAND, dummy_demand)
    print_subsection("Parametros do modelo LP")
    print(f"  Variaveis: {n_i * n_j} continuas (x_ij >= 0)")
    print(f"  Restricoes de igualdade: {n_i} (oferta) + {n_j} (demanda) = {n_i + n_j}")
    print(f"  b_oferta = {SUPPLY.tolist()}")
    print(f"  b_demanda (com ficticio) = {demand_full.tolist()}")
    print(f"  Vetor c (flattened 3x12, linha por linha):")
    print(f"    {costs_full.flatten().tolist()}")

    print_subsection("Chamada do resolvedor")
    print("  scipy.optimize.linprog(")
    print("      c,")
    print("      A_eq=A_eq,  # shape (15, 36)")
    print("      b_eq=b_eq,  # [500, 750, 400, 112, 85, ..., 432]")
    print("      bounds=[(0, None)] * 36,")
    print("      method='highs'")
    print("  )")

    # ---- Solve -------------------------------------------------------------
    sol = solve()
    print(f"\n  Status: {sol['status']}")

    # ---- Solution ----------------------------------------------------------
    print_section("Solucao - Exercicio 4")

    alloc = sol["allocation"]
    dummy = sol["dummy_allocation"]

    # Full solution matrix including dummy column
    alloc_full = np.hstack([alloc, dummy.reshape(n_i, 1)])
    print_subsection("Matriz de alocacao completa (inclui coluna ficticia)")
    print_matrix(
        alloc_full.tolist(), CENTERS, WAREHOUSES + [DUMMY_LABEL], decimals=2
    )

    print_subsection("Envio ao destino ficticio (excesso nao alocado a armazens reais)")
    for center, qty in zip(CENTERS, dummy):
        print(f"  {center}: {format_number(qty)} t")

    print_subsection("Verificacao de balanco")
    all_ok = True
    for i, center in enumerate(CENTERS):
        sent = float(alloc[i].sum() + dummy[i])
        diff = abs(sent - SUPPLY[i])
        ok = diff < 1e-4
        if not ok:
            all_ok = False
        status = "OK" if ok else f"ERRO (dif={diff:.2e})"
        print(f"  {center}: enviou {format_number(sent)} t  "
              f"(capacidade {int(SUPPLY[i])})  {status}")
    for j, wh in enumerate(WAREHOUSES):
        received = float(alloc[:, j].sum())
        diff = abs(received - DEMAND[j])
        ok = diff < 1e-4
        if not ok:
            all_ok = False
        status = "OK" if ok else f"ERRO (dif={diff:.2e})"
        print(f"  {wh}: recebeu {format_number(received)} t  "
              f"(demanda {int(DEMAND[j])})  {status}")
    print(f"\n  Balanco: {'TODAS as restricoes satisfeitas' if all_ok else 'RESTRICAO VIOLADA'}")
    print(f"\n  Custo total otimo: {format_number(sol['total_cost'])}")

    if json_path is not None:
        _export_json(sol, json_path)
        print(f"\n  Solucao exportada para: {json_path}")


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def _export_json(sol: dict, path: str | Path) -> None:
    """Write the transportation solution to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    alloc = sol["allocation"]
    dummy = sol["dummy_allocation"]
    record = {
        "exercicio": 4,
        "centers": CENTERS,
        "warehouses": WAREHOUSES,
        "allocation": {
            CENTERS[i]: {
                WAREHOUSES[j]: round(float(alloc[i, j]), 4)
                for j in range(len(WAREHOUSES))
            }
            for i in range(len(CENTERS))
        },
        "dummy_allocation": {
            CENTERS[i]: round(float(dummy[i]), 4) for i in range(len(CENTERS))
        },
        "total_cost": round(sol["total_cost"], 4),
        "status": sol["status"],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
