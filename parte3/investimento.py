"""Exercise 6 - Capital investment selection with logical constraints.

Ten projects with binary selection variables.  Maximise total present value
subject to budget, manager limit, and six logical dependency/exclusivity rules.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from formatting import format_number, print_section, print_subsection

# ---------------------------------------------------------------------------
# Problem data
# ---------------------------------------------------------------------------

INVESTMENTS: np.ndarray = np.array(
    [20000, 35000, 70000, 90000, 60000, 150000, 170000, 80000, 90000, 100000],
    dtype=float,
)
PRESENT_VALUES: np.ndarray = np.array(
    [25000, 40000, 100000, 80000, 60000, 130000, 160000, 100000, 130000, 150000],
    dtype=float,
)
BUDGET: float = 400_000.0
MAX_PROJECTS: int = 5
N: int = 10
PROJECTS: list[str] = [f"Proj {i + 1}" for i in range(N)]


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

def solve() -> dict:
    """Solve the investment selection MILP (maximise total VP).

    Returns
    -------
    dict
        y (list[int] of 0/1), selected (list[int] of 0-based indices),
        n_selected, total_investment, total_vp, status.
    """
    # Minimise -VP  (equivalent to maximising VP)
    c = -PRESENT_VALUES.astype(float)

    # Inequality constraints A_ub @ y <= b_ub
    # Rows: a, b, c, d, e, f1, f2, budget, manager
    A_ub = np.zeros((9, N))
    b_ub = np.zeros(9)

    # a) y[1] - y[0] <= 0
    A_ub[0, [1, 0]] = [1.0, -1.0];   b_ub[0] = 0.0

    # b) y[2] + y[3] <= 1
    A_ub[1, [2, 3]] = [1.0, 1.0];    b_ub[1] = 1.0

    # c) y[4] - y[3] <= 0
    A_ub[2, [4, 3]] = [1.0, -1.0];   b_ub[2] = 0.0

    # d) y[5] + y[6] <= 1
    A_ub[3, [5, 6]] = [1.0, 1.0];    b_ub[3] = 1.0

    # e) y[7] + y[8] + y[9] <= 1
    A_ub[4, [7, 8, 9]] = [1.0, 1.0, 1.0];   b_ub[4] = 1.0

    # f1) y[7]+y[8]+y[9] - y[5] - y[6] <= 0
    A_ub[5, [7, 8, 9, 5, 6]] = [1.0, 1.0, 1.0, -1.0, -1.0];   b_ub[5] = 0.0

    # f2) y[7]+y[8]+y[9] - y[2] - y[3] <= 0
    A_ub[6, [7, 8, 9, 2, 3]] = [1.0, 1.0, 1.0, -1.0, -1.0];   b_ub[6] = 0.0

    # g) sum(INV * y) <= BUDGET
    A_ub[7] = INVESTMENTS;   b_ub[7] = BUDGET

    # h) sum(y) <= MAX_PROJECTS
    A_ub[8] = np.ones(N);    b_ub[8] = float(MAX_PROJECTS)

    lc = LinearConstraint(A_ub, lb=-np.inf * np.ones(9), ub=b_ub)
    bounds = Bounds(lb=np.zeros(N), ub=np.ones(N))
    integrality = np.ones(N)

    result = milp(c, constraints=lc, integrality=integrality, bounds=bounds)

    if result.status != 0:
        raise RuntimeError(
            f"milp retornou status {result.status}: {result.message}"
        )

    y = np.round(result.x).astype(int)
    selected = [i for i in range(N) if y[i] == 1]

    return {
        "y": y.tolist(),
        "selected": selected,
        "n_selected": len(selected),
        "total_investment": float(INVESTMENTS[selected].sum()),
        "total_vp": float(PRESENT_VALUES[selected].sum()),
        "status": result.message,
    }


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def run(json_path: str | Path | None = None) -> None:
    """Print model data, solve, and display solution for Exercise 6."""
    print_section("Exercicio 6 - Selecao de Investimentos")

    # ---- Input data --------------------------------------------------------
    print_subsection("Dados dos projetos")
    print(f"  {'Projeto':<10}  {'INV ($)':<12}  {'VP ($)':<12}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*12}")
    for i in range(N):
        print(f"  {PROJECTS[i]:<10}  {int(INVESTMENTS[i]):>12,}  "
              f"{int(PRESENT_VALUES[i]):>12,}")
    print(f"\n  Orcamento total:    $ {int(BUDGET):>12,}")
    print(f"  Limite de gerentes: {MAX_PROJECTS} projetos")

    print_subsection("Restricoes logicas")
    print("  a) y_2 <= y_1   (Proj 2 complementar ao Proj 1)")
    print("  b) y_3 + y_4 <= 1   (Projs 3 e 4 mutuamente exclusivos)")
    print("  c) y_5 <= y_4   (Proj 5 complementar ao Proj 4)")
    print("  d) y_6 + y_7 <= 1   (Projs 6 e 7 mutuamente exclusivos)")
    print("  e) y_8 + y_9 + y_10 <= 1   (Projs 8, 9, 10 mutuamente exclusivos)")
    print("  f) y_8+y_9+y_10 <= y_6+y_7   e   y_8+y_9+y_10 <= y_3+y_4")
    print("  g) sum(INV_j * y_j) <= 400.000")
    print("  h) sum(y_j) <= 5")

    c_neg = (-PRESENT_VALUES).astype(int)
    print_subsection("Parametros do modelo MILP")
    print(f"  Variaveis: {N} binarias y_j in {{0,1}}")
    print(f"  Restricoes de desigualdade: 7 logicas + 1 orcamento + 1 gerentes = 9")
    print(f"  Funcao objetivo: min (-VP)  ==>  max VP")
    print(f"  Vetor c = -VP: {c_neg.tolist()}")
    print(f"  Vetor INV: {INVESTMENTS.astype(int).tolist()}")

    print_subsection("Chamada do resolvedor")
    print("  scipy.optimize.milp(")
    print("      c,")
    print("      constraints=LinearConstraint(A_ub, lb=-inf, ub=b_ub),  # shape (9,10)")
    print("      integrality=np.ones(10),")
    print("      bounds=Bounds(0, 1)")
    print("  )")

    # ---- Solve -------------------------------------------------------------
    sol = solve()
    print(f"\n  Status: {sol['status']}")

    # ---- Solution ----------------------------------------------------------
    print_section("Solucao - Exercicio 6")

    y = sol["y"]
    selected = sol["selected"]

    print_subsection("Resultado por projeto")
    print(f"  {'Projeto':<10}  {'INV ($)':<12}  {'VP ($)':<12}  Selecionado")
    print(f"  {'-'*10}  {'-'*12}  {'-'*12}  -----------")
    for i in range(N):
        sel = "SIM" if y[i] else "nao"
        print(f"  {PROJECTS[i]:<10}  {int(INVESTMENTS[i]):>12,}  "
              f"{int(PRESENT_VALUES[i]):>12,}  {sel}")

    print(f"\n  Projetos selecionados: {[PROJECTS[i] for i in selected]}")
    print(f"  Numero de projetos:    {sol['n_selected']} / {MAX_PROJECTS}")
    print(f"  Investimento total:    $ {int(sol['total_investment']):,} "
          f"/ $ {int(BUDGET):,}")
    print(f"  Valor presente total:  $ {int(sol['total_vp']):,}")

    print_subsection("Verificacao das restricoes logicas")
    y_arr = np.array(y)
    checks = [
        ("a) y_2 <= y_1",           bool(y_arr[1] <= y_arr[0])),
        ("b) y_3 + y_4 <= 1",       bool(y_arr[2] + y_arr[3] <= 1)),
        ("c) y_5 <= y_4",           bool(y_arr[4] <= y_arr[3])),
        ("d) y_6 + y_7 <= 1",       bool(y_arr[5] + y_arr[6] <= 1)),
        ("e) y_8+y_9+y_10 <= 1",    bool(y_arr[7] + y_arr[8] + y_arr[9] <= 1)),
        ("f1) y8+9+10 <= y6+7",     bool(y_arr[7] + y_arr[8] + y_arr[9]
                                        <= y_arr[5] + y_arr[6])),
        ("f2) y8+9+10 <= y3+4",     bool(y_arr[7] + y_arr[8] + y_arr[9]
                                        <= y_arr[2] + y_arr[3])),
        ("g) Orcamento",            bool(sol["total_investment"] <= BUDGET + 1e-4)),
        ("h) Limite de gerentes",   bool(sol["n_selected"] <= MAX_PROJECTS)),
    ]
    all_ok = all(ok for _, ok in checks)
    for label, ok in checks:
        print(f"  {label}: {'OK' if ok else 'VIOLADO'}")
    print(f"\n  Resultado geral: "
          f"{'TODAS as restricoes satisfeitas' if all_ok else 'RESTRICAO VIOLADA'}")

    if json_path is not None:
        _export_json(sol, json_path)
        print(f"\n  Solucao exportada para: {json_path}")


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def _export_json(sol: dict, path: str | Path) -> None:
    """Write the investment solution to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "exercicio": 6,
        "projects": PROJECTS,
        "y": sol["y"],
        "selected": [PROJECTS[i] for i in sol["selected"]],
        "n_selected": sol["n_selected"],
        "total_investment": sol["total_investment"],
        "budget": BUDGET,
        "total_vp": sol["total_vp"],
        "max_projects": MAX_PROJECTS,
        "status": sol["status"],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
