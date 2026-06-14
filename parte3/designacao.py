"""Exercise 5 - Worker-to-task assignment problem.

Six workers must be assigned to six tasks (one-to-one).
Solved with scipy.optimize.milp (binary variables) and verified with
scipy.optimize.linear_sum_assignment.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linear_sum_assignment, milp

from formatting import format_number, print_matrix, print_section, print_subsection

# ---------------------------------------------------------------------------
# Problem data
# ---------------------------------------------------------------------------

TIMES: np.ndarray = np.array([
    [13, 22, 19, 21, 16, 20],   # T1
    [18, 17, 24, 18, 22, 27],   # T2
    [20, 22, 23, 24, 17, 31],   # T3
    [14, 19, 13, 30, 23, 22],   # T4
    [21, 14, 17, 25, 15, 23],   # T5
    [17, 23, 18, 20, 16, 24],   # T6
], dtype=float)

WORKERS: list[str] = [f"T{i + 1}" for i in range(6)]
TASKS: list[str] = [f"J{j + 1}" for j in range(6)]


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

def solve() -> dict:
    """Solve the 6×6 assignment problem with milp and verify with linear_sum_assignment.

    Returns
    -------
    dict
        assignment (list[int] of length 6, worker i -> task index),
        times (list[float]),
        total_time (float),
        verify_total (float from linear_sum_assignment),
        status (str).
    """
    n = 6
    n_vars = n * n   # 36 binary variables x[i,j]

    c = TIMES.flatten().astype(float)

    # Equality constraints: each row sums to 1, each column sums to 1
    A = np.zeros((2 * n, n_vars))
    for i in range(n):
        A[i, i * n:(i + 1) * n] = 1.0          # worker i row sum
    for j in range(n):
        for i in range(n):
            A[n + j, i * n + j] = 1.0           # task j column sum

    ones = np.ones(2 * n)
    lc = LinearConstraint(A, lb=ones, ub=ones)
    bounds = Bounds(lb=np.zeros(n_vars), ub=np.ones(n_vars))
    integrality = np.ones(n_vars)

    result = milp(c, constraints=lc, integrality=integrality, bounds=bounds)

    if result.status != 0:
        raise RuntimeError(
            f"milp retornou status {result.status}: {result.message}"
        )

    x = np.round(result.x).reshape(n, n)
    assignment = [int(np.argmax(x[i])) for i in range(n)]
    times = [float(TIMES[i, assignment[i]]) for i in range(n)]
    total_time = sum(times)

    # Independent verification
    row_ind, col_ind = linear_sum_assignment(TIMES)
    verify_total = float(TIMES[row_ind, col_ind].sum())

    return {
        "assignment": assignment,
        "times": times,
        "total_time": total_time,
        "verify_total": verify_total,
        "status": result.message,
    }


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def run(json_path: str | Path | None = None) -> None:
    """Print model data, solve, and display solution for Exercise 5."""
    n = 6

    print_section("Exercicio 5 - Designacao de Trabalhadores")

    # ---- Input data --------------------------------------------------------
    print_subsection("Dados de entrada")
    print(f"  Trabalhadores: {', '.join(WORKERS)}")
    print(f"  Tarefas: {', '.join(TASKS)}")

    print_subsection("Matriz de tempos c_ij (minutos)")
    print_matrix(TIMES.tolist(), WORKERS, TASKS, decimals=0)

    c = TIMES.flatten().astype(int)
    print_subsection("Parametros do modelo MILP")
    print(f"  Variaveis: {n * n} binarias x_ij in {{0,1}}")
    print(f"  Restricoes de igualdade: {n} (por trabalhador) + {n} (por tarefa) = {2*n}")
    print(f"  Funcao objetivo: min sum_ij c_ij * x_ij  (minimizar tempo total)")
    print(f"  Vetor c (flattened 6x6): {c.tolist()}")
    print(f"  Limites: 0 <= x_ij <= 1 (integralidade forcada)")

    print_subsection("Chamada do resolvedor")
    print("  scipy.optimize.milp(")
    print("      c,")
    print("      constraints=LinearConstraint(A, lb=1, ub=1),  # A shape (12, 36)")
    print("      integrality=np.ones(36),")
    print("      bounds=Bounds(0, 1)")
    print("  )")
    print()
    print("  Verificacao independente:")
    print("  scipy.optimize.linear_sum_assignment(TIMES)")

    # ---- Solve -------------------------------------------------------------
    sol = solve()
    print(f"\n  Status milp: {sol['status']}")

    # ---- Solution ----------------------------------------------------------
    print_section("Solucao - Exercicio 5")

    print_subsection("Matriz de designacao X (binaria)")
    x_matrix = [[0] * n for _ in range(n)]
    for i, task_idx in enumerate(sol["assignment"]):
        x_matrix[i][task_idx] = 1
    print_matrix(x_matrix, WORKERS, TASKS, decimals=0)

    print_subsection("Designacoes otimas")
    header = f"  {'Trabalhador':<15}  {'Tarefa':<8}  Tempo (min)"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for i, (task_idx, t) in enumerate(zip(sol["assignment"], sol["times"])):
        print(f"  {WORKERS[i]:<15}  {TASKS[task_idx]:<8}  {int(t)}")

    print(f"\n  Tempo total (milp):                  {int(sol['total_time'])} min")
    print(f"  Verificacao (linear_sum_assignment): {int(sol['verify_total'])} min")
    match = abs(sol["total_time"] - sol["verify_total"]) < 1e-4
    print(f"  Resultado: {'OK - valores coincidem' if match else 'DIVERGENCIA'}")

    if json_path is not None:
        _export_json(sol, json_path)
        print(f"\n  Solucao exportada para: {json_path}")


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def _export_json(sol: dict, path: str | Path) -> None:
    """Write the assignment solution to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "exercicio": 5,
        "workers": WORKERS,
        "tasks": TASKS,
        "assignment": [
            {
                "worker": WORKERS[i],
                "task": TASKS[sol["assignment"][i]],
                "time_min": sol["times"][i],
            }
            for i in range(6)
        ],
        "total_time_min": sol["total_time"],
        "verify_total_min": sol["verify_total"],
        "status": sol["status"],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
