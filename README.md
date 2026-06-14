# lista_mma - MILP Exercise List

Solver implementations for a Mixed-Integer Linear Programming (MILP) exercise list,
organised by part. Each part is self-contained and can be run independently.

## Project structure

```
lista_mma/
  parte1/    # Branch-and-Bound solver (Exercises 1, 2 and 4)
  parte3/    # Transport, assignment and investment solvers (Exercises 4, 5 and 6)
  parte4/    # MST (Prim, Kruskal) and max-flow (Edmonds-Karp) solvers (Exercises 1, 2 and 3)
  requirements.txt
```

## Requirements

- Python 3.13
- `numpy >= 1.26`
- `scipy >= 1.12`
- `networkx >= 3.0` (Parte 4 only, for cross-verification)

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

---

## Parte 3 - Transport, Assignment and Investment Solvers

Solves three optimisation exercises using `scipy.optimize.linprog` and
`scipy.optimize.milp` (HiGHS backend).

### Exercises

| Exercise | Type | Model | Solver |
|----------|------|-------|--------|
| 4 | Unbalanced transportation (Deise-Luzia) | LP - equality constraints | `linprog` |
| 5 | Worker-to-task assignment (6x6) | Binary IP | `milp` + `linear_sum_assignment` |
| 6 | Capital investment selection (10 projects) | Binary IP with logical constraints | `milp` |

### Usage

Run from the `parte3/` directory:

```bash
cd parte3
python run.py --exercicio {4,5,6} [--json-out PATH]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--exercicio` | yes | Exercise number: 4, 5, or 6 |
| `--json-out` | no | Path for JSON solution export |

### Examples

```bash
# Exercise 4 - transportation problem with JSON export
python run.py --exercicio 4 --json-out output/transporte_ex4.json

# Exercise 5 - assignment problem
python run.py --exercicio 5 --json-out output/designacao_ex5.json

# Exercise 6 - investment selection
python run.py --exercicio 6 --json-out output/investimento_ex6.json
```

### Optimal results

| Exercise | Result |
|----------|--------|
| 4 | Total transport cost = 16,678.50 |
| 5 | Minimum total assignment time = 99 min |
| 6 | Maximum present value = $ 475,000 (projects 1,2,3,7,10; investment $ 395,000) |

### Running tests

```bash
cd parte3
python -m pytest tests/ -v
```

Expected: 18 tests pass (supply/demand balance, assignment validity,
logical constraint satisfaction, budget and manager limit checks).

---

## Parte 4 - MST and Max-Flow Solvers

Solves three graph optimisation exercises from scratch, with full
decision logs and cross-verification against NetworkX.

### Exercises

| Exercise | Algorithm | Graph | Nodes | Edges/Arcs |
|----------|-----------|-------|-------|------------|
| 1 | Prim + Kruskal (MST) | G1 - undirected | 12 | 19 |
| 2 | Prim + Kruskal (MST) | G2 - undirected | 15 | 28 |
| 3 | Edmonds-Karp (max flow) | G3 - directed | 12 | 19 |

### Usage

Run from the `parte4/` directory:

```bash
cd parte4
python run.py --exercicio {1,2,3} [--prim-start NODE] [--json-out PATH]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--exercicio` | yes | - | Exercise number: 1, 2 (MST) or 3 (max flow) |
| `--prim-start` | no | `1` | Starting node for Prim's algorithm (MST only) |
| `--json-out` | no | - | Export solution to JSON file |

### Examples

```bash
# Exercise 1 - MST for G1 with JSON export
python run.py --exercicio 1 --json-out output/mst_ex1.json

# Exercise 2 - MST for G2 with custom Prim start node
python run.py --exercicio 2 --prim-start 8

# Exercise 3 - max flow for G3 with JSON export
python run.py --exercicio 3 --json-out output/maxflow_ex3.json
```

### Optimal results

| Exercise | Result |
|----------|--------|
| 1 | MST weight = 74 |
| 2 | MST weight = 86 |
| 3 | Max flow = 11 (source: node 1, sink: node 12) |

### Running tests

```bash
cd parte4
python -m pytest tests/ -v
```

Expected: 25 tests pass (UnionFind correctness, Kruskal/Prim edge count and
weight matching NetworkX, flow conservation, min-cut capacity, arc capacity
bounds).
