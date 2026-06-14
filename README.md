# lista_mma - MILP Exercise List

Solver implementations for a Mixed-Integer Linear Programming (MILP) exercise list,
organised by part. Each part is self-contained and can be run independently.

## Project structure

```
lista_mma/
  parte1/    # Branch-and-Bound solver (Exercises 1, 2 and 4)
  parte3/    # (to be added)
  parte4/    # (to be added)
  requirements.txt
```

## Requirements

- Python 3.13
- `numpy >= 1.26`
- `scipy >= 1.12`

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Parte 1 - Branch-and-Bound Solver

Solves three MILP exercises using a custom Branch-and-Bound (B&B) algorithm built on
top of `scipy.optimize.linprog` (HiGHS backend). The optimal solution is verified
against `scipy.optimize.milp` after every full run.

### Exercises

| Exercise | Type | Sense | Integer variables |
|----------|------|-------|------------------|
| 1 | Pure integer | Maximisation | x1, x2, x3, x4 |
| 2 | Mixed integer | Maximisation | x1, x2, x4 (x3 continuous) |
| 4 | Mixed integer | Minimisation | x1, x3 (x2 continuous) |

### Search strategies

| Flag | Strategy | Description |
|------|----------|-------------|
| `dfs` (default) | Depth-first | LIFO stack, lower branch explored first |
| `bfs` | Breadth-first | FIFO queue, lower branch explored first |

### Usage

Run from the `parte1/` directory:

```bash
cd parte1
python run.py --exercicio {1,2,4} [--strategy {dfs,bfs}] [--max-nodes N] [--json-out PATH]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--exercicio` | yes | - | Exercise number: 1, 2, or 4 |
| `--strategy` | no | `dfs` | Search strategy: `dfs` or `bfs` |
| `--max-nodes` | no | unlimited | Stop after processing N nodes |
| `--json-out` | no | - | Export B&B tree to JSON file |

### Examples

```bash
# Exercise 1 - full DFS run with JSON export
python run.py --exercicio 1 --strategy dfs --json-out output/arvore_ex1.json

# Exercise 2 - breadth-first search
python run.py --exercicio 2 --strategy bfs

# Exercise 4 - inspect first 5 nodes only
python run.py --exercicio 4 --max-nodes 5

# All three exercises with JSON export
python run.py --exercicio 1 --json-out output/arvore_ex1.json
python run.py --exercicio 2 --json-out output/arvore_ex2.json
python run.py --exercicio 4 --json-out output/arvore_ex4.json
```

### Output format

Each B&B node is printed as a box after the full tree is resolved:

```
Subproblema 3
  Ramo: x1 <= 2, x2 >= 3
  Z  = 17,00
  x1 = 2
  x2 = 3,5
  x3 = 0
  Status: Solução Candidata
```

Possible statuses: `Ramificado`, `Solução Candidata`, `Solução Infactível`,
`Inferior a melhor ja obtida`, `Solução Otima`.

The run ends with a summary line confirming the B&B result matches the reference solver:

```
=== Resultado - Exercicio 1 ===
Nos resolvidos: 11
Solucao otima: x1=0,  x2=0,  x3=1,  x4=2  |  Z = 20,00
Verificacao milp: Z = 20,00  v
```

### Running tests

```bash
cd parte1
python -m pytest tests/ -v
```

Expected: 25 tests pass (unit tests for integrality check, branching variable selection,
number formatting, and end-to-end verification against `scipy.optimize.milp`).
