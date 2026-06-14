# lista_mma — MILP Exercise List

Solver implementations for the MILP exercise list, organised by part.

## Requirements

- Python 3.13
- Dependencies: `numpy>=1.26`, `scipy>=1.12`

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Parte 1 — Branch-and-Bound Solver

Solves three MILP exercises using a Branch-and-Bound algorithm with `linprog` (HiGHS).

### Usage

```bash
cd parte1
python run.py --exercicio {1,2,4} [--strategy {dfs,bfs}] [--max-nodes N] [--json-out PATH]
```

### Examples

```bash
# Exercise 1, depth-first search, export tree to JSON
python run.py --exercicio 1 --strategy dfs --json-out output/arvore_ex1.json

# Exercise 2, breadth-first search
python run.py --exercicio 2 --strategy bfs

# Exercise 4, limit to 5 nodes
python run.py --exercicio 4 --max-nodes 5
```

### Running tests

```bash
cd parte1
python -m pytest tests/ -v
```
